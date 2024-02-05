
from twisted.internet import reactor
from app.protocols import SocketPolicyServer
from app.server import SnowflakeWorld
from app.logging import Console

import traceback
import logging
import config

logging.basicConfig(
    handlers=[Console],
    level=logging.DEBUG if config.ENABLE_DEBUG_LOGGING else logging.INFO
)

if __name__ == "__main__":
    try:
        policy_server = SocketPolicyServer()
        world_server = SnowflakeWorld()
        world_server.listen(config.PORT)

        if not config.DISABLE_POLICY_SERVER:
            policy_server.listenTCP(843)

        reactor.run()
    except Exception as e:
        traceback.print_exc()
        logging.fatal(f'Failed to start server: {e}')
        exit(1)
