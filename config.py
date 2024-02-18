
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
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

    PORT = int(os.environ.get('PORT', '7002'))
    VERSION = os.environ.get('VERSION', 'FY15-20150206 (4954)r')

    MEDIA_LOCATION = os.environ.get('MEDIA_LOCATION')
    MEDIA_DOMAIN = MEDIA_LOCATION.replace('http://', '').replace('https://', '')

    APPLY_WINDOWMANAGER_OFFSET = os.environ.get('APPLY_WINDOWMANAGER_OFFSET', 'False').lower() == 'true'
    ENABLE_DEBUG_PLAYERS = os.environ.get('ENABLE_DEBUG_PLAYERS', 'False').lower() == 'true'
    ENABLE_DEBUG_LOGGING = os.environ.get('ENABLE_DEBUG_LOGGING', 'False').lower() == 'true'
    DISABLE_POLICY_SERVER = os.environ.get('DISABLE_POLICY_SERVER', 'False').lower() == 'true'
    DISABLE_ENEMY_AI = os.environ.get('DISABLE_ENEMY_AI', 'False').lower() == 'true'
    DISABLE_REWARDS = os.environ.get('DISABLE_REWARDS', 'False').lower() == 'true'
    DISABLE_STAMPS = os.environ.get('DISABLE_STAMPS', 'False').lower() == 'true'
    ENABLE_BETA = os.environ.get('ENABLE_BETA', 'False').lower() == 'true'
    if ENABLE_BETA:
        DISABLE_STAMPS = False

    BASE_URL = f'{MEDIA_LOCATION}/game/mpassets/'
    CARDS_ASSET_LOCATION = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/'
    WINDOW_MANAGER_LOCATION = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/windowManager/windowmanager.swf'
    WINDOW_BASEURL = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows'
    ASSET_BASEURL = f'{MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/assets'
except Exception as e:
    print(
        f'Failed to load configuration: {e}\n'
        'Please check your .env file!'
    )
    exit(1)
