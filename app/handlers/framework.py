
from app.engine import Penguin, Instance

@Instance.events.register("/framework")
def framework(client: Penguin, json: dict):
    Instance.triggers.call(json['triggerName'], client, json)

@Instance.triggers.register('payloadBILogAction')
def funnel(client: Penguin, json: dict):
    # TODO: Implement funnel analysis
    pass
