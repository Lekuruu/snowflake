
from __future__ import annotations
from twisted.internet import reactor, task

async def delay(seconds: int | float, clock=reactor) -> None:
    """Yield to the Twisted reactor for given seconds"""
    if seconds <= 0:
        return

    await task.deferLater(clock, seconds, lambda: None)
