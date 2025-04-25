
from urllib.parse import urlparse
from dotenv import load_dotenv

import os

load_dotenv(override=True)

try:
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    REDIS_DB = int(os.environ.get('REDIS_DB', '0'))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')

    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', '5432'))
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    POSTGRES_DBNAME = os.environ.get('POSTGRES_DBNAME', POSTGRES_USER)

    PORT = int(os.environ.get('PORT', '7002'))
    VERSION = os.environ.get('VERSION', 'FY15-20150206 (4954)r')

    WEBSOCKET_ENABLED = os.environ.get('WEBSOCKET_ENABLED', 'False').lower() == 'true'
    WEBSOCKET_PORT = int(os.environ.get('WEBSOCKET_PORT', '7003'))

    MEDIA_LOCATION = os.environ.get('MEDIA_LOCATION')
    MEDIA_DOMAIN = urlparse(MEDIA_LOCATION).hostname

    MATCHMAKING_TIMEOUT = int(os.environ.get('MATCHMAKING_TIMEOUT', '30'))
    ALLOW_FORCESTART_SNOW = os.environ.get('ALLOW_FORCESTART_SNOW', 'False').lower() == 'true'
    ALLOW_FORCESTART_TUSK = os.environ.get('ALLOW_FORCESTART_TUSK', 'True').lower() == 'true'

    POLICY_DOMAIN = os.environ.get('POLICY_DOMAIN', '*')
    POLICY_PORT = os.environ.get('POLICY_PORT', '*')
    ENABLE_POLICY_SERVER = os.environ.get('ENABLE_POLICY_SERVER', 'False').lower() == 'true'

    APPLY_WINDOWMANAGER_OFFSET = os.environ.get('APPLY_WINDOWMANAGER_OFFSET', 'False').lower() == 'true'
    ENABLE_DEBUG_LOGGING = os.environ.get('ENABLE_DEBUG_LOGGING', 'False').lower() == 'true'
    DISABLE_AUTHENTICATION = os.environ.get('DISABLE_AUTHENTICATION', 'False').lower() == 'true'
    DISABLE_ENEMY_AI = os.environ.get('DISABLE_ENEMY_AI', 'False').lower() == 'true'
    DISABLE_REWARDS = os.environ.get('DISABLE_REWARDS', 'False').lower() == 'true'
    DISABLE_STAMPS = os.environ.get('DISABLE_STAMPS', 'False').lower() == 'true'
    ENABLE_BETA = os.environ.get('ENABLE_BETA', 'False').lower() == 'true'

    BASE_URL = f'{MEDIA_LOCATION}/game/mpassets/'
    CARDS_ASSET_LOCATION = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/'
    WINDOW_MANAGER_LOCATION = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/windowManager/windowmanager.swf'
    WINDOW_BASEURL = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows'
    ASSET_BASEURL = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/assets'

    PLAYERSELECT_SWF = (
        'cardjitsu_snowplayerselect.swf'
        if not ENABLE_BETA else
        'cardjitsu_snowplayerselectbeta.swf'
    )
except Exception as e:
    print(
        f'Failed to load configuration: {e}\n'
        'Please check your .env file!'
    )
    exit(1)
