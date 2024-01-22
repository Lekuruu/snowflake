
from app.engine import SnowflakeEngine
from app.logging import Console

import logging

logging.basicConfig(
    handlers=[Console],
    level=logging.DEBUG
)

if __name__ == "__main__":
    SnowflakeEngine().run()
