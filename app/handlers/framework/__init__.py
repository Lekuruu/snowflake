
from app.engine import Penguin, Instance

from . import game, windowmanager, matchmaking

@Instance.events.register("/framework")
def framework(client: Penguin, json: dict):
    Instance.triggers.call(json['triggerName'], client, json)

@Instance.triggers.register('payloadBILogAction')
def action(client: Penguin, json: dict):
    Instance.actions.call(json['action'], client, json)
