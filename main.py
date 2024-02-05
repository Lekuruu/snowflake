
from twisted.internet import reactor
from app.engine import Instance as Server
from app.protocols import SocketPolicyServer
from app.logging import Console

import logging
import config

logging.basicConfig(
    handlers=[Console],
    level=logging.DEBUG if config.ENABLE_DEBUG_LOGGING else logging.INFO
)

if __name__ == "__main__":
    try:
        if not config.DISABLE_POLICY_SERVER:
            reactor.listenTCP(843, SocketPolicyServer())

        reactor.listenTCP(config.PORT, Server)
        reactor.run()
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        exit(1)
