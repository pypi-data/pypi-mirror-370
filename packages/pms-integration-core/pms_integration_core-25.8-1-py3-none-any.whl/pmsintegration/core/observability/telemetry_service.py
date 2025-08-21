import atexit

from prometheus_client import start_http_server

from pmsintegration.platform.config import ConfigEnvironment


def initialize(env: ConfigEnvironment):
    config = env.find_matched("platform.observability")
    server, server_thread = start_http_server(
        addr=config.get("host"),
        port=config.get("port"),
    )

    # Register shutdown at exit
    atexit.register(server.shutdown)
