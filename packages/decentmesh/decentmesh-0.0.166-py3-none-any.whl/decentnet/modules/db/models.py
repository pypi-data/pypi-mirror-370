import time
from datetime import datetime, timedelta, UTC
from sqlite3 import IntegrityError

import sqlalchemy
from sqlalchemy import (REAL, Boolean, Column, ForeignKey, Integer,
                        LargeBinary, String, UniqueConstraint, select, BLOB, DateTime)
from sqlalchemy.orm import declarative_base, mapped_column

from decentnet.modules.db.constants import USING_ASYNC_DB

Base = declarative_base()


class BlockTable(Base):
    __tablename__ = 'block'

    block_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    blockchain_id = Column(Integer,
                           ForeignKey("blockchain.blockchain_id", ondelete="CASCADE"),
                           index=True)
    index = Column(Integer, nullable=False, index=True)
    hash = Column(LargeBinary, nullable=False)
    previous_hash = Column(LargeBinary, nullable=False)
    timestamp = Column(REAL, nullable=False, default=time.time())
    data = Column(LargeBinary, nullable=False)
    nonce = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Block(id={self.block_id}, hash='{self.hash}', previous_hash='{self.previous_hash}', " \
               f"timestamp='{self.timestamp}', data='{self.data}')>"


class BlockSignatureTable(Base):
    __tablename__ = "block_signature"
    block_id = Column(Integer, ForeignKey("block.block_id", ondelete="CASCADE"),
                      primary_key=True, index=True)
    signature = Column(String(256), nullable=False)


class BlockchainTable(Base):
    __tablename__ = "blockchain"
    beam_id = Column(Integer, ForeignKey("beam.id", ondelete="CASCADE"), index=True)
    blockchain_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(REAL, default=time.time(), nullable=False)
    version = Column(String(16), nullable=False)

    difficulty = Column(String(128), nullable=False)


class ForeignKeys(Base):
    __tablename__ = 'foreign_key'
    id = Column(Integer, primary_key=True, autoincrement=True)
    public_key = Column(String(256), unique=True, index=True)
    identity = Column(String(256), nullable=True)
    description = Column(String(128), nullable=True)
    can_encrypt = Column(Boolean, nullable=False)
    received_at = Column(REAL, default=time.time())


class OwnedKeys(Base):
    __tablename__ = 'owned_key'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    alias = Column(String(128), unique=True, index=True, nullable=True)
    private_key = Column(String(256), unique=True)
    public_key = Column(String(256), unique=True, index=True)
    description = Column(String(128))
    can_encrypt = Column(Boolean, nullable=False)
    generated_at = Column(REAL, default=time.time())


class BeamTable(Base):
    __tablename__ = "beam"
    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain_id = mapped_column(ForeignKey("blockchain.blockchain_id"), unique=True,
                                  index=True)
    beam_hash = Column(String(256), unique=True, index=True)
    owner_public_key = Column(String(256), index=True)
    target_public_key = Column(String(256), index=True)
    timestamp = Column(REAL, default=time.time(), nullable=False)

    @staticmethod
    async def save(beam, pub_key: str, target_key: str, conn_bc_id: int, comm_bc_id: int):
        from decentnet.modules.db.base import session_scope

        def add_or_update_beam(session, b_found=None):
            if beam.beam_id and b_found:
                if target_key == "NOT_KNOWN":
                    b_found.target_public_key = target_key
            else:
                # Add new BeamTable entry
                bdb = BeamTable(
                    blockchain_id=conn_bc_id,
                    beam_hash=beam.hash,
                    owner_public_key=pub_key,
                    target_public_key=target_key
                )
                session.add(bdb)
                return bdb

        async def update_blockchain_connections_async(session, bdb):
            # Retrieve the blockchain connections asynchronously
            blockchain_conn = await session.get(BlockchainTable, conn_bc_id)
            blockchain_comm = await session.get(BlockchainTable, comm_bc_id)

            blockchain_comm.beam_id = blockchain_conn.beam_id = beam.beam_id = bdb.id

        def update_blockchain_connections_sync(session, bdb):
            # Retrieve the blockchain connections synchronously
            blockchain_conn = session.get(BlockchainTable, conn_bc_id)
            blockchain_comm = session.get(BlockchainTable, comm_bc_id)

            blockchain_comm.beam_id = blockchain_conn.beam_id = beam.beam_id = bdb.id

        if USING_ASYNC_DB:
            async with session_scope() as session:
                result = await session.execute(
                    select(BeamTable).where(
                        (BeamTable.id == beam.beam_id) & (
                                (BeamTable.owner_public_key == pub_key) |
                                (BeamTable.target_public_key == pub_key)
                        )
                    )
                )
                b_found = result.scalar_one_or_none()
                bdb = add_or_update_beam(session, b_found)
                await session.flush()  # Ensure the database is updated

                await update_blockchain_connections_async(session, bdb)
        else:
            with session_scope() as session:
                result = session.execute(
                    select(BeamTable).where(
                        (BeamTable.id == beam.beam_id) & (
                                (BeamTable.owner_public_key == pub_key) |
                                (BeamTable.target_public_key == pub_key)
                        )
                    )
                )
                b_found = result.scalar_one_or_none()
                bdb = add_or_update_beam(session, b_found)
                session.flush()  # Ensure the database is updated

                update_blockchain_connections_sync(session, bdb)


class Edge(Base):
    __tablename__ = 'edge'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    pub_key = Column(String(256), nullable=False, comment="Edge public key", index=True)
    target = Column(String(256), nullable=True, comment="Target public key", index=True)
    capacity = Column(Integer, nullable=False)
    difficulty = Column(Integer, nullable=False,
                        default=0)
    connected = Column(Boolean, nullable=False, default=True)
    added_at = Column(REAL, default=time.time())
    # Ensure that the combination of pub_key and target is unique
    __table_args__ = (UniqueConstraint('pub_key', 'target', name='pub_target_uk'),)


class NodeInfoTable(Base):
    __tablename__ = "node_info"
    # beacon or edge id mapped
    id = Column(Integer, primary_key=True, autoincrement=True)
    edge_id = mapped_column(ForeignKey("edge.id"), unique=True,
                            index=True, nullable=True)
    ipv4 = Column(String(64), nullable=True)
    port = Column(Integer, nullable=True)
    ipv6 = Column(String(128), nullable=True)
    mac = Column(String(17),
                 nullable=True)
    pub_key = Column(String(256), nullable=False, index=True, unique=True)
    last_ping = Column(REAL, default=time.time())


def one_hour_from_now():
    return datetime.now(UTC) + timedelta(minutes=5)


class Mail(Base):
    __tablename__ = "mailbox"
    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(256), nullable=True, index=True)
    block = Column(BLOB, nullable=False)
    expire_at = Column(DateTime, nullable=False, default=one_hour_from_now)


class AliveBeam(Base):
    __tablename__ = "alive_beam"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pub_key = Column(String(256), nullable=False, index=True, unique=True)
    ready = Column(Boolean, nullable=False, default=False)
    added_at = Column(REAL, default=time.time())

    @classmethod
    async def mark_beam_ready(cls, pub_key: str, ready: bool):
        from decentnet.modules.db.base import session_scope

        if USING_ASYNC_DB:
            async with session_scope() as session:
                try:
                    # Asynchronously query the database
                    result = await session.execute(
                        select(cls).where(cls.pub_key == pub_key)
                    )
                    csd = result.scalar_one_or_none()

                    if not csd:
                        ab = AliveBeam(pub_key=pub_key, ready=ready)
                        session.add(ab)
                    else:
                        csd.ready = ready
                except (IntegrityError, sqlalchemy.exc.IntegrityError):
                    pass  # Handle or log the exception as needed
        else:
            with session_scope() as session:
                try:
                    # Synchronously query the database
                    result = session.execute(
                        select(cls).where(cls.pub_key == pub_key)
                    )
                    csd = result.scalar_one_or_none()

                    if not csd:
                        ab = AliveBeam(pub_key=pub_key, ready=ready)
                        session.add(ab)
                    else:
                        csd.ready = ready

                except (IntegrityError, sqlalchemy.exc.IntegrityError):
                    pass  # Handle or log the exception as needed
