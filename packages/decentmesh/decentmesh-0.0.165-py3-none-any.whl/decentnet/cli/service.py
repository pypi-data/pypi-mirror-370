import asyncio
import multiprocessing

import click
import rich
from sqlalchemy import select

from decentnet.consensus.dev_constants import METRICS, RUN_IN_DEBUG
from decentnet.modules.banner.banner import orig_text
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.constants import USING_ASYNC_DB
from decentnet.modules.db.models import AliveBeam, OwnedKeys
from decentnet.modules.migrate.migrate_agent import MigrateAgent
from decentnet.modules.seed_connector.SeedsAgent import SeedsAgent
from decentnet.modules.tcp.server import TCPServer
from decentnet.utils.key_tools import generate_impl

try:
    import sentry_sdk

    if not RUN_IN_DEBUG:
        sentry_sdk.init(
            dsn="https://71d6a0d07fac5d2f072b6c7151321766@o4507850186096640.ingest.de.sentry.io/4507850892378192",
        )
except (ModuleNotFoundError, ImportError):
    rich.print("Sentry is disabled due to import error.")


@click.group()
def service():
    pass


@service.command()
@click.argument('host', type=click.STRING)
@click.argument('port', type=int)
def start(host: str, port: int):
    rich.print(orig_text)
    MigrateAgent.do_migrate()

    if METRICS:
        from decentnet.modules.monitoring.metric_server import \
            metric_server_start
        prom_proc = multiprocessing.Process(target=metric_server_start, name="Metric server",
                                            daemon=True)
        prom_proc.start()
    from decentnet import __version__
    rich.print(f"Starting DecentMesh v{__version__.__version__}")
    asyncio.run(__generate_keys())

    server = TCPServer(host, port)

    rich.print("Connecting to DecentMesh seed nodes...")
    SeedsAgent(host, port, METRICS)

    server.run()


async def __generate_keys():
    async def handle_async(session):
        # Perform async database operations
        result = await session.execute(select(AliveBeam))
        beams = result.scalars().all()

        for beam in beams:
            await session.delete(beam)

        await session.commit()

        result = await session.execute(select(OwnedKeys).limit(1))
        owned_key = result.scalar_one_or_none()

        if owned_key is None:
            print("Generating first keys for communication")
            await generate_keys()

    def handle_sync(session):
        # Perform sync database operations
        result = session.execute(select(AliveBeam))
        beams = result.scalars().all()

        for beam in beams:
            session.delete(beam)

        session.commit()

        result = session.execute(select(OwnedKeys).limit(1))
        owned_key = result.scalar_one_or_none()

        if owned_key is None:
            print("Generating first keys for communication")
            generate_keys()

    # Switch between async and sync context managers
    if USING_ASYNC_DB:
        async with session_scope() as session:
            await handle_async(session)
    else:
        with session_scope() as session:
            handle_sync(session)


async def generate_keys():
    """Generate keys based on the async or sync mode."""
    suc = await generate_impl(private_key_file=None, public_key_file=None, description="First Key", sign=True)
    suc *= await generate_impl(private_key_file=None, public_key_file=None, description="First Key",
                               sign=True)
    suc *= await generate_impl(private_key_file=None, public_key_file=None, description="First Key",
                               sign=True)
    suc *= await generate_impl(private_key_file=None, public_key_file=None, description="First Key",
                               sign=False)
    if not suc:
        rich.print("[red]Failed to generate keys.[/red]")
        return
    rich.print("[green]Generated new keys and saved to database[/green]")
