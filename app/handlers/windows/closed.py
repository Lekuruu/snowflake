
from app.engine import Penguin, Instance

@Instance.triggers.register('windowClosed')
def on_window_closed(client: Penguin, data: dict):
    window_name = data['windowUrl'].split('/')[-1]
    client.logger.debug(f'Closed window: "{window_name}"')

    window = client.window_manager.get_window(window_name)
    window.loaded = False

    if window.on_close:
        window.on_close(client)

    try:
        del client.window_manager[window_name]
    except KeyError:
        pass