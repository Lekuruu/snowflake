
from app.engine.penguin import Penguin
from app import session

@session.framework.register('windowClosed')
def on_window_closed(client: Penguin, data: dict):
    window_name = data['windowUrl'].split('/')[-1]

    window = client.get_window(window_name)

    try:
        del client.window_manager[window_name]
    except KeyError:
        pass

    window.set_loaded(False)

    if window.on_close:
        window.on_close(client)
