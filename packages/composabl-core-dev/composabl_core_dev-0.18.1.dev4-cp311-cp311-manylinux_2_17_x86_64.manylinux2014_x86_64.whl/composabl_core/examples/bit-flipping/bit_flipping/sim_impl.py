# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict, SupportsFloat, Tuple

import gymnasium as gym
from gymnasium.envs.registration import EnvSpec

import composabl_core.utils.logger as logger_util
from bit_flipping.sim import BitFlippingSim
from composabl_core.agent.scenario import Scenario
from composabl_core.networking.sim.server_composabl import ServerComposabl

logger = logger_util.get_logger(__name__)


class SimImpl(ServerComposabl):
    def __init__(self):
        self.sim = None

    async def make(self, env_id: str, env_init: dict) -> EnvSpec:
        n = env_init.get("n", 3)
        self.sim = BitFlippingSim(N=n)

    async def sensor_space_info(self) -> gym.Space:
        return self.sim.sensor_space

    async def action_space_info(self) -> gym.Space:
        return self.sim.action_space

    async def action_space_sample(self) -> Any:
        return self.sim.action_space.sample()

    async def reset(self) -> Tuple[Any, Dict[str, Any]]:
        sensors, info = self.sim.reset()
        return sensors, info

    async def step(
        self, action
    ) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        return self.sim.step(action)

    async def close(self) -> None:
        self.sim = None

    async def set_scenario(self, scenario) -> None:
        pass

    async def get_scenario(self) -> Scenario:
        pass

    async def get_render(self) -> Any:
        if self.sim is None:
            return ""

        return self.sim.render()
