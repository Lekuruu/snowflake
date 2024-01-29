
from app.engine import Penguin, Instance

@Instance.events.register("/framework")
def framework(client: Penguin, json: dict):
    Instance.triggers.call(json['triggerName'], client, json)

@Instance.triggers.register('payloadBILogAction')
def action(client: Penguin, json: dict):
    Instance.actions.call(json['action'], client, json)
