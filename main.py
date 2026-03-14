
from twisted.internet import reactor
from app.protocols import SocketPolicyServer, WebSocketWrapper
from app.server import SnowflakeWorld
from app.logging import Console

import traceback
import logging
import signal
import config

logging.basicConfig(
    handlers=[Console],
    level=logging.DEBUG if config.ENABLE_DEBUG_LOGGING else logging.INFO
)
world_server: SnowflakeWorld
policy_server: SocketPolicyServer

def on_shutdown(*args):
    """Kick all players from the server, before the reactor stops"""
    world_server.logger.warning("Shutting down...")
    world_server.shutting_down = True

    for player in world_server.players:
        player.send_to_room()

    reactor.callLater(0.1, reactor.stop)

def main():
    global world_server, policy_server

    world_server = SnowflakeWorld()
    world_server.listen(config.PORT)

    if config.ENABLE_POLICY_SERVER:
        policy_server = SocketPolicyServer(
            config.POLICY_DOMAIN,
            config.POLICY_PORT
        )
        policy_server.listen(843)

    if config.WEBSOCKET_ENABLED:
        # Use txws to wrap tcp factory
        ws_factory = WebSocketWrapper(world_server)
        ws_factory.listen(config.WEBSOCKET_PORT)

    reactor.run()

if __name__ == "__main__":
    # Handle shutdown signals to kick players before the reactor stops
    signal.signal(signal.SIGINT, on_shutdown)

    try:
        main()
    except Exception as e:
        traceback.print_exc()
        logging.fatal(f'An error error occurred: {e}')
        exit(1)
