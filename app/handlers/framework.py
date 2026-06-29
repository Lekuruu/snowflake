
from app.engine import Penguin
from app import session

@session.events.register("/framework")
async def framework(client: Penguin, json: dict):
    await session.framework.call(json['triggerName'], client, json)

@session.framework.register('payloadBILogAction')
async def funnel(client: Penguin, json: dict):
    # TODO: Implement funnel analysis
    pass
