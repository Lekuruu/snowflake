
from __future__ import annotations

from app import engine
from app.data import (
    ClientAction,
    MessageType,
    EventType
)

from typing import Dict

import config
import json

class SWFWindow:
    def __init__(
        self,
        client: engine.Penguin,
        url: str | None = None,
        name: str | None = None,
        layer: str = 'topLayer'
    ) -> None:
        if not name:
            # "filename.swf"
            name = url.split('/')[-1]

        elif not url:
            # Default location
            url = f'http://{config.MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/{name}'

        assert url or name, 'You must provide either a url or a name for the window.'

        self.name = name
        self.url = url
        self.client = client
        self.layer = layer # TODO: topLayer, bottomLayer, toolLayer
        self.asset_path = '' # TODO

    def __repr__(self) -> str:
        return f"<SWF ({self.name})>"

    def send(self, content: dict = {}, message_type = MessageType.RECEIVED_JSON, **kwargs):
        content.update(kwargs)
        self.client.send_tag(
            'UI_CLIENTEVENT',
            self.client.server.world_id,
            message_type.value,
            json.dumps(content)
        )

    def load(self, initial_payload: dict = None, **kwargs):
        self.client.logger.debug(f'Loading window {self}')
        self.send(
            {
                'windowUrl': self.url,
                'layerName': self.layer,
                'assetPath': self.asset_path,
                'initializationPayload': initial_payload,
                'action': ClientAction.LOAD_WINDOW.value,
                'type': EventType.PLAY_ACTION.value
            },
            **kwargs
        )

    def close(self, **kwargs):
        self.client.logger.debug(f'Closing window: {self}')
        self.send(
            {
                'targetWindow': self.url,
                'action': ClientAction.CLOSE_WINDOW.value,
                'type': EventType.PLAY_ACTION.value,
            },
            **kwargs
        )

    def send_payload(self, trigger_name: str, payload: dict = {}, type = EventType.IMMEDIATE, **kwargs):
        self.client.logger.debug(f'Sending payload to window: \n{json.dumps(payload, indent=4)}')
        self.send(
            {
                'jsonPayload': payload,
                'targetWindow': self.url,
                'triggerName': trigger_name,
                'action': ClientAction.PAYLOAD.value,
                'type': type.value
            },
            **kwargs
        )

    def send_action(self, action: str, type = EventType.IMMEDIATE, **kwargs):
        self.client.logger.debug(f'Sending action to window: {action}')
        self.send(
            {
                'action': action,
                'type': type.value
            },
            **kwargs
        )

class WindowManager(Dict[str, SWFWindow]):
    def __init__(
        self,
        client: engine.Penguin,
        swf_url: str = f'http://{config.MEDIA_LOCATION}/game/mpassets//minigames/cjsnow/en_US/deploy/swf/windowManager/windowmanager.swf'
    ) -> None:
        self.element_name = "WindowManagerSwf"
        self.command_prefix = "/framework"
        self.element_id = client.server.world_id
        self.swf_url = swf_url
        self.client = client

        self.parent_id = 0
        self.swf_x = 0
        self.swf_y = 0
        self.swf_width = 0
        self.swf_height = 0

        self.loaded = False
        self.ready = False

    def __setitem__(self, name: str, window: SWFWindow) -> None:
        self.client.logger.debug(f'Loading new window: {window}')
        return super().__setitem__(name, window)
    
    def get_window(self, name: str | None = None, url: str | None = None):
        assert url or name, 'You must provide either a url or a name for the window.'

        # TODO: Refactor this
        if (name in self):
            return self[name]

        elif (url != None) and (url.split('/')[-1] in self):
            return self[url]

        self[name] = (
            SWFWindow(self.client, url, name)
        )

        return self[name]

    def load(self):
        self.client.logger.debug(f'Loading window manager...')
        self.client.send_tag(
            'UI_CROSSWORLDSWFREF',
            self.element_id,
            self.parent_id,
            self.element_name,
            self.swf_x,
            self.swf_y,
            self.swf_width,
            self.swf_height,
            0, # TODO: this is some kind of bool, that does nothing ig?
            self.swf_url,
            self.command_prefix
        )
        self.loaded = True

        self['windowmanager.swf'] = SWFWindow(
            self.client,
            self.swf_url,
            'windowmanager.swf'
        )
