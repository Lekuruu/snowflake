
from app.events import EventHandler, FrameworkHandler
from app.objects import AssetCollection
from app.data.postgres import Postgres
from redis import Redis

import config

framework = FrameworkHandler()
events = EventHandler()

sound_assets = AssetCollection()
assets = AssetCollection()

database = Postgres(
    config.POSTGRES_USER,
    config.POSTGRES_DBNAME,
    config.POSTGRES_PASSWORD,
    config.POSTGRES_HOST,
    config.POSTGRES_PORT
)

redis = Redis(
    config.REDIS_HOST,
    config.REDIS_PORT,
    config.REDIS_DB,
    config.REDIS_PASSWORD
)
