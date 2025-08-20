# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import ray

from composabl_core.examples.actor_counter_nested import (
    DemoCounterActorNested,
    DemoCounterNested,
)


class DemoCounter:
    def __init__(self, counter: int = 0):
        self.counter = counter
        self.counter_nested = DemoCounterNested(counter)

    def get_counter(self):
        return self.counter

    def get_counter_nested(self):
        return ray.get(self.counter_nested.get_counter())

    def set_counter_nested(self, value: int):
        self.counter_nested.set_counter(value)

    async def get_counter_async(self):
        return self.counter

    def increment(self) -> None:
        self.counter += 1

    async def increment_async(self) -> None:
        self.counter += 1

    def throw(self):
        raise ValueError("This is a sync test error")

    async def throw_async(self):
        raise ValueError("This is an async test error")


class DemoCounterActor:
    def __init__(self, counter: int = 0):
        self.counter = counter
        self.counter_nested = ray.remote(DemoCounterActorNested).remote(counter)

    def get_counter(self):
        return self.counter

    def get_counter_nested(self):
        return ray.get(self.counter_nested.get_counter.remote())

    def set_counter_nested(self, value: int):
        self.counter_nested.set_counter.remote(value)

    async def get_counter_async(self):
        return self.counter

    def increment(self) -> None:
        self.counter += 1

    async def increment_async(self) -> None:
        self.counter += 1

    def throw(self):
        raise ValueError("This is a sync test error")

    async def throw_async(self):
        raise ValueError("This is an async test error")
