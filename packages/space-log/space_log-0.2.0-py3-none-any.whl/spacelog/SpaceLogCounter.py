from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from spacelog.SpaceLogClient import SpaceLogClient


class SpaceLogCounter:
    def __init__(self, name: str, client: SpaceLogClient):
        self.name = name
        self.client = client

    def increment(self, value: float):
        self.client.update_counter(self.name, value, increment=True)

    def increment_by_one(self):
        self.increment(1.0)

    def set(self, value: float):
        self.client.update_counter(self.name, value, increment=False)

    def reset(self, value: float = 0.0):
        self.set(value)
