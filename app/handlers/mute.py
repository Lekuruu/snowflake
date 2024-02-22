
from app.engine import Penguin
from app import session

@session.framework.register("muteFromCP")
def mute_sounds(client: Penguin, data: dict):
    client.mute_sounds = True
