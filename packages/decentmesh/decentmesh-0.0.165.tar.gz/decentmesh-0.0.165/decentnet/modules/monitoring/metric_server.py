import asyncio
import logging

import httpx
from aiohttp import web
from hypercorn import Config
from hypercorn.asyncio import serve
from prometheus_client import Histogram

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import PROMETHEUS_HOST, PROMETHEUS_PORT
from decentnet.consensus.metrics_constants import (METRICS_SERVER_HOST,
                                                   METRICS_SERVER_PORT)
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.req_queue.reques_queue import ReqQueue

# Declare your metrics globally
block_difficulty_bits = Histogram('block_difficulty_bits', 'Difficulty of blockchain bits')
block_difficulty_memory = Histogram('block_difficulty_memory', 'Difficulty of blockchain memory')
block_difficulty_time = Histogram('block_difficulty_time', 'Difficulty of blockchain time')
block_difficulty_parallel = Histogram('block_difficulty_parallel', 'Difficulty of blockchain parallel')
data_header_ratio = Histogram('data_header_ratio', 'Header/Data Ratio')
prom_block_process_time = Histogram('block_process_time', 'Time spent processing a block')
prom_data_received = Histogram("data_received_for_relay", "Data received for relaying")
prom_path_length = Histogram("path_length", "Path length for relaying data")
prom_data_published = Histogram("data_published_for_relay", "Data published for relaying")

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class AsyncMetricServer:
    """Class-based async metric server using GET requests."""

    @classmethod
    async def handle_metrics(cls, request):
        """Async handler for incoming metric updates via GET request."""
        try:
            # Parse query parameters
            metric_name = request.query.get('name')
            metric_value = request.query.get('value')
            metric_func = request.query.get('func')

            # Ensure metric_value is properly cast to float or int
            if metric_value is not None:
                metric_value = float(metric_value)

            # Use globals() to dynamically get the variable by name and call observe on it
            if metric_name in globals() and metric_value is not None:
                metric = globals()[metric_name]
                getattr(metric, metric_func)(metric_value)
                return web.Response(status=200,
                                    text=f"Metric {metric_name} updated with value {metric_value}\n")
            else:
                return web.Response(status=400, text=f"Metric {metric_name} not found or invalid value\n")
        except Exception as e:
            return web.Response(status=500, text=f"Server error: {str(e)}\n")

    async def init_app(self):
        """Initialize the aiohttp app and set up routes."""
        app = web.Application()
        app.add_routes([web.get('/metrics', self.handle_metrics)])  # GET endpoint for metrics
        return app

    @classmethod
    async def start_prometheus_server(cls):
        logger.debug("Starting Prometheus client with Hypercorn...")
        import prometheus_client

        # Create the ASGI app for Prometheus metrics
        app = prometheus_client.make_asgi_app()

        # Configure Hypercorn to serve the app
        config = Config()
        config.lifespan = "off"
        config.bind = [f"{PROMETHEUS_HOST}:{PROMETHEUS_PORT}"]

        # Start the Hypercorn server asynchronously
        await serve(app, config)

    async def start_server(self, port=METRICS_SERVER_PORT):
        """Start the aiohttp web server."""

        app = await self.init_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, METRICS_SERVER_HOST, port)
        logger.debug(f"Running multiprocess collector metrics server on http://{METRICS_SERVER_HOST}:{port}")
        await site.start()
        await self.start_prometheus_server()

        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Keep the server running


def metric_server_start():
    server = AsyncMetricServer()
    asyncio.run(server.start_server(port=METRICS_SERVER_PORT))


async def ping(timeout=0.1):
    try:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            await client.get(f"http://{METRICS_SERVER_HOST}:{METRICS_SERVER_PORT}/metrics", timeout=timeout)
            return True  # Host is alive
    except asyncio.TimeoutError:
        return False  # Timeout occurred
    except Exception:
        return False  # Other exceptions, consider the host down


async def send_metric(name, value, metric_type="observe"):
    ReqQueue.append(_send_metric(name, value, metric_type))


async def _send_metric(name, value, metric_type="observe", timeout=0.1):
    params = {'name': name, 'func': metric_type, 'value': value}

    try:
        async with httpx.AsyncClient(follow_redirects=False) as client:
            response = await client.get(
                f"http://{METRICS_SERVER_HOST}:{METRICS_SERVER_PORT}/metrics",
                params=params, timeout=timeout)
            return response.status_code == 200  # Return True if status is 200, else False
    except Exception as e:
        print(f"Request failed: {e}")
        return False


if __name__ == '__main__':
    # Initialize and start the server
    _server = AsyncMetricServer()
    asyncio.run(_server.start_server(port=METRICS_SERVER_PORT))
