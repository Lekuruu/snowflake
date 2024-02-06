
from app.engine import Penguin
from app import session

@session.framework.register('windowReady')
def on_window_ready(client: Penguin, data: dict):
    window_name = data['windowUrl'].split('/')[-1]

    window = client.get_window(window_name)
    window.loaded = True

    if window.on_load:
        window.on_load(client)
