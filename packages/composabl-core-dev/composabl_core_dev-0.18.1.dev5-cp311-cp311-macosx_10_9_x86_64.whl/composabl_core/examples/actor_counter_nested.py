# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


class DemoCounterNested:
    def __init__(self, counter: int = 0):
        self.counter = counter

    def get_counter(self):
        return self.counter

    def set_counter(self, value: int):
        self.counter = value


class DemoCounterActorNested:
    def __init__(self, counter: int = 0):
        self.counter = counter

    def get_counter(self):
        return self.counter

    def set_counter(self, value: int):
        self.counter = value
