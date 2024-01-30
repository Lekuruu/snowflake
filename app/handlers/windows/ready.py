
from app.engine import Penguin, Instance

@Instance.triggers.register('windowReady')
def on_window_ready(client: Penguin, data: dict):
    window_name = data['windowUrl'].split('/')[-1]
    client.logger.debug(f'Loaded window: "{window_name}"')

    window = client.window_manager.get_window(window_name)
    window.loaded = True

    if window.on_load:
        window.on_load(client)
