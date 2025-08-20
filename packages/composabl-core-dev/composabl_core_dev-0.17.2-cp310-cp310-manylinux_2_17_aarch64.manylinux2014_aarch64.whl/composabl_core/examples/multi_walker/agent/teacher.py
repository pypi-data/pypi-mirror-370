# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from typing import Dict

from composabl_core.agent.skill.skill_teacher import SkillTeacher
from composabl_core.examples.multi_walker.agent.sensors_walker_0 import sensors_walker_0
from composabl_core.examples.multi_walker.agent.sensors_walker_1 import sensors_walker_1
from composabl_core.examples.multi_walker.agent.sensors_walker_2 import sensors_walker_2


class WalkerTeacher0(SkillTeacher):
    """
    We start at 10 reward and count down to 0 the goal is that the agent stays above or equal to 0
    this means it learned to cound +1 each time
    """

    def __init__(self, sensor_name: str = "counter", *args, **kwargs):
        self.past_obs = None
        self.counter = 10
        self.sensor_name = sensor_name  # depends on the space type (see classes below)

    async def compute_reward(self, transformed_sensors: Dict, action, sim_reward):
        return sim_reward

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        return None

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return False

    async def compute_termination(self, transformed_sensors, action):
        return False

    async def transform_sensors(self, sensors: Dict, action):
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        return action

    async def filtered_sensor_space(self):
        return [sensor.name for sensor in sensors_walker_0]


class WalkerTeacher1(SkillTeacher):
    """
    We start at 10 reward and count down to 0 the goal is that the agent stays above or equal to 0
    this means it learned to cound +1 each time
    """

    def __init__(self, sensor_name: str = "counter", *args, **kwargs):
        self.past_obs = None
        self.counter = 10
        self.sensor_name = sensor_name  # depends on the space type (see classes below)

    async def compute_reward(self, transformed_sensors: Dict, action, sim_reward):
        return sim_reward

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        return None

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return False

    async def compute_termination(self, transformed_sensors, action):
        return False

    async def transform_sensors(self, sensors: Dict, action):
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        return action

    async def filtered_sensor_space(self):
        return [sensor.name for sensor in sensors_walker_1]


class WalkerTeacher2(SkillTeacher):
    """
    We start at 10 reward and count down to 0 the goal is that the agent stays above or equal to 0
    this means it learned to cound +1 each time
    """

    def __init__(self, sensor_name: str = "counter", *args, **kwargs):
        self.past_obs = None
        self.counter = 10
        self.sensor_name = sensor_name  # depends on the space type (see classes below)

    async def compute_reward(self, transformed_sensors: Dict, action, sim_reward):
        return sim_reward

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        return None

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return False

    async def compute_termination(self, transformed_sensors, action):
        return False

    async def transform_sensors(self, sensors: Dict, action):
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        return action

    async def filtered_sensor_space(self):
        return [sensor.name for sensor in sensors_walker_2]
