
from app.engine import Instance as Server
from app.logging import Console

import logging
import config

logging.basicConfig(
    handlers=[Console],
    level=logging.DEBUG if config.ENABLE_DEBUG_LOGGING else logging.INFO
)

if __name__ == "__main__":
    Server.run()
