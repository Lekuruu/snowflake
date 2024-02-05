
from app.engine import Penguin
from app import session

@session.events.register("/framework")
def framework(client: Penguin, json: dict):
    session.framework.call(json['triggerName'], client, json)

@session.framework.register('payloadBILogAction')
def funnel(client: Penguin, json: dict):
    # TODO: Implement funnel analysis
    pass
