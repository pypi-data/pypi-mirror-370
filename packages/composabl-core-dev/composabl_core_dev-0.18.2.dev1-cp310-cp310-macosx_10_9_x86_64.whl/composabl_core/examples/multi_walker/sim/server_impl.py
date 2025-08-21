# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict, SupportsFloat, Tuple

import gymnasium as gym
from gymnasium.envs.registration import EnvSpec

from composabl_core import spaces as ComposablSpaces
from composabl_core.agent.scenario import Scenario
from composabl_core.networking.sim.server_composabl import ServerComposabl

from pettingzoo.sisl import multiwalker_v9


class ServerImpl(ServerComposabl):
    def __init__(self, *args, **kwargs):
        self.env_init = kwargs.get("env_init", {})
        self.env = multiwalker_v9.parallel_env(render_mode="human")
        self.action_space = None
        self.obs_space = None

    async def make(self, env_id: str, env_init: dict) -> EnvSpec:
        spec = {"id": "starship", "max_episode_steps": 400}
        return spec

    async def sensor_space_info(self) -> gym.Space:
        obs_space_1 = self.env.observation_space("walker_0")
        obs_space_2 = self.env.observation_space("walker_1")
        obs_space_3 = self.env.observation_space("walker_2")
        obs_space = ComposablSpaces.Dict(
            {"walker_0": obs_space_1, "walker_1": obs_space_2, "walker_2": obs_space_3}
        )

        self.obs_space = obs_space
        return self.obs_space

    async def action_space_info(self) -> gym.Space:
        action_space_0 = self.env.action_space("walker_0")
        action_space_1 = self.env.action_space("walker_1")
        action_space_2 = self.env.action_space("walker_2")
        action_space = ComposablSpaces.Dict(
            {
                "walker_0": action_space_0,
                "walker_1": action_space_1,
                "walker_2": action_space_2,
            }
        )

        self.action_space = action_space
        return self.action_space

    async def action_space_sample(self) -> Any:
        return self.action_space.sample()

    async def reset(self) -> Tuple[Any, Dict[str, Any]]:
        sensors, info = self.env.reset()
        return sensors, info

    async def step(
        self, action
    ) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        return self.env.step(action)

    async def close(self):
        self.env.close()

    async def set_scenario(self, scenario):
        self.env.scenario = scenario

    async def get_scenario(self):
        if self.env.scenario is None:
            return Scenario({"dummy": 0})

        return self.env.scenario

    async def get_render(self):
        return self.env.render()
