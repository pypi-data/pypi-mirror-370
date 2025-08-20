import asyncio
import logging
from functools import lru_cache

import networkx as nx
import sqlalchemy
from nacl.signing import VerifyKey
from networkx.exception import NetworkXError
from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.constants import USING_ASYNC_DB
from decentnet.modules.db.models import Edge
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class FlowNetwork:
    _instance = None  # Class variable to hold the single instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FlowNetwork, cls).__new__(cls)
            # Call the initialization only once.
            cls._instance.__init_once__(*args, **kwargs)
        return cls._instance

    def __init_once__(self, _save_to_db=True):
        self.graph = nx.Graph()
        logger.debug("Rebuilding FlowNetwork from DB")
        if _save_to_db:
            asyncio.run(self.rebuild_flow_network())

    async def rebuild_flow_network(self):
        async def handle_async():
            # Fetch edges asynchronously
            result = await session.execute(select(Edge))
            edges = result.scalars().all()

            # Process each edge
            for edge in edges:
                self.graph.add_edge(edge.pub_key, edge.target, capacity=edge.capacity, flow=0)

            # Log the result
            logger.debug(f"Flow network rebuilt from {len(edges)} edges")

        def handle_sync():
            # Fetch edges synchronously
            result = session.execute(select(Edge))
            edges = result.scalars().all()

            # Process each edge
            for edge in edges:
                self.graph.add_edge(edge.pub_key, edge.target, capacity=edge.capacity, flow=0)

            # Log the result
            logger.debug(f"Flow network rebuilt from {len(edges)} edges")

        # Switch between async and sync context managers
        if USING_ASYNC_DB:
            async with session_scope() as session:
                await handle_async()
        else:
            with session_scope() as session:
                handle_sync()

    async def add_edge(self, edge_pub_key, target, capacity,
                       _save_to_db: bool = True):
        """
        Adding edge and nodes
        edges will be added to work both ways
        :param edge_pub_key: Edge public key
        :param target: Target public key
        :param capacity: Connection capacity ( abstract unit ) TODO
        :param _save_to_db:
        :return:
        """
        if edge_pub_key == "NOT_KNOWN" or target == "NOT_KNOWN":
            return False

        self.graph.add_edge(edge_pub_key, target, capacity=capacity, flow=0)

        logger.debug(f"Connected edge {edge_pub_key} => {target}")

        if _save_to_db:
            await FlowNetwork.save_edge_to_db(edge_pub_key, target, capacity)

    async def rm_edge(self, edge_pub_key: str | bytes | VerifyKey, target: bytes | VerifyKey,
                      _save_to_db: bool = True):
        """
        Adding edge and nodes
        edges will be added to work both ways
        :param edge_pub_key: Edge public key
        :param target: Target public key
        :param capacity: Connection capacity ( abstract unit ) TODO
        :param _save_to_db:
        :return:
        """
        if edge_pub_key == "NOT_KNOWN" or target == "NOT_KNOWN":
            return False

        if isinstance(target, bytes):
            target = KeyManager.key_to_base64(target)
        elif isinstance(target, VerifyKey):
            target = AsymCrypt.verifying_key_to_string(target)

        if isinstance(edge_pub_key, bytes):
            edge_pub_key = KeyManager.key_to_base64(target)
        elif isinstance(edge_pub_key, VerifyKey):
            edge_pub_key = AsymCrypt.verifying_key_to_string(target)

        try:
            self.graph.remove_edge(edge_pub_key, target)
        except NetworkXError:
            logger.warning(f"Edge {edge_pub_key} => {target} not found in graph")

        logger.debug(f"Removed edge {edge_pub_key} => {target}")

        if _save_to_db:
            await FlowNetwork.remove_edge_from_db(edge_pub_key, target)

    @lru_cache(maxsize=128)
    def get_path(self, source, sink):
        max_flow = 0

        path = nx.shortest_path(self.graph, source=source, target=sink,
                                weight='capacity')
        # Find the minimum capacity on the augmenting path
        capacities = (self.graph[u][v]['capacity'] for u, v in zip(path, path[1:]))

        try:
            min_capacity = min(capacities)
        except ValueError:
            min_capacity = 0
        # Update the flow along the augmenting path
        for u, v in zip(path, path[1:]):
            self.graph[u][v]['capacity'] -= min_capacity
            self.graph[u][v]['flow'] += min_capacity
            self.graph[v][u]['flow'] -= min_capacity
        max_flow += min_capacity

        return path, max_flow

    @classmethod
    async def save_edge_to_db(cls, source_pub_key, target_pub_key, capacity):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                try:
                    stmt = select(
                        exists().where(Edge.pub_key == source_pub_key).where(Edge.target == target_pub_key))
                    result = await session.execute(stmt)
                    exists_query = result.scalar()
                    if exists_query:
                        return False
                    edge_to = Edge(pub_key=source_pub_key, target=target_pub_key, capacity=capacity)
                    session.add(edge_to)
                    await session.commit()
                    return True
                except (IntegrityError, sqlalchemy.exc.IntegrityError):
                    logging.debug(
                        f"Attempted to insert an edge {edge_to.pub_key} => {edge_to.target} that exists")
                    await session.rollback()  # Roll back to a clean state
        else:
            with session_scope() as session:
                try:
                    exists_query = session.query(exists().where(Edge.pub_key == source_pub_key).where(
                        Edge.target == target_pub_key)).scalar()
                    if exists_query:
                        return False
                    edge_to = Edge(pub_key=source_pub_key, target=target_pub_key, capacity=capacity)
                    session.add(edge_to)
                    session.commit()
                    return True
                except (IntegrityError, sqlalchemy.exc.IntegrityError):
                    logging.debug(
                        f"Attempted to insert an edge {edge_to.pub_key} => {edge_to.target} that exists")
                    session.rollback()  # Roll back to a clean state

    @classmethod
    async def remove_edge_from_db(cls, source_pub_key, target_pub_key):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                try:
                    # Query the edge to delete
                    stmt = select(Edge).where(Edge.pub_key == source_pub_key, Edge.target == target_pub_key)
                    result = await session.execute(stmt)
                    edge_to_remove = result.scalar_one_or_none()

                    if edge_to_remove:
                        await session.delete(edge_to_remove)
                        await session.commit()
                        return True
                    return False
                except Exception as e:
                    logging.debug(f"Failed to remove the edge {source_pub_key} => {target_pub_key}: {str(e)}")
                    await session.rollback()
                    return False
        else:
            with session_scope() as session:
                try:
                    # Query the edge to delete
                    edge_to_remove = session.query(Edge).filter_by(pub_key=source_pub_key,
                                                                   target=target_pub_key).one_or_none()

                    if edge_to_remove:
                        session.delete(edge_to_remove)
                        session.commit()
                        return True
                    return False
                except Exception as e:
                    logging.debug(f"Failed to remove the edge {source_pub_key} => {target_pub_key}: {str(e)}")
                    session.rollback()
                    return False

    def forward_flow(self, path, min_capacity):
        for u, v in zip(path, path[1:]):
            self.graph[u][v]['capacity'] -= min_capacity
            self.graph[u][v]['flow'] += min_capacity
            self.graph[v][u]['flow'] -= min_capacity

    async def bulk_save_db(self):
        if USING_ASYNC_DB:
            async def save_async():
                try:
                    async with session_scope() as session:
                        for u, v, data in self.graph.edges(data=True):
                            edge = Edge(source=u, target=v, capacity=data['capacity'], flow=data['flow'])
                            session.add(edge)

                except (IntegrityError, sqlalchemy.exc.IntegrityError):
                    logging.warning("Attempted to insert an edge that exists")
                    await session.rollback()

            return save_async()
        else:
            try:
                with session_scope() as session:
                    for u, v, data in self.graph.edges(data=True):
                        edge = Edge(source=u, target=v, capacity=data['capacity'], flow=data['flow'])
                        session.add(edge)
            except (IntegrityError, sqlalchemy.exc.IntegrityError):
                logging.warning("Attempted to insert an edge that exists")
                session.rollback()

    def compute_maximum_flow(self, source, sink):
        max_flow = self.get_path(source, sink)

        # Forward flow through the network based on the computed maximum flow
        while True:
            # Find an augmenting path using Breadth-First Search
            path = nx.shortest_path(self.graph, source=source, target=sink,
                                    weight='capacity')
            if not path:
                break

            # Find the minimum capacity on the augmenting path
            min_capacity = min(
                self.graph[u][v]['capacity'] for u, v in zip(path, path[1:]))

            # Forward flow along the augmenting path
            self.forward_flow(path, min_capacity)

        return path, max_flow
