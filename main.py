
from app.engine import Instance as Server
from app.logging import Console

import logging

logging.basicConfig(
    handlers=[Console],
    level=logging.DEBUG
)

if __name__ == "__main__":
    Server.run()
