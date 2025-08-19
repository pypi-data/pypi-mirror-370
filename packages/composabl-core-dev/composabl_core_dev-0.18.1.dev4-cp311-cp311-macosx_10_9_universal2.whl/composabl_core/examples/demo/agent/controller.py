# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import random
from typing import Dict

import numpy as np

from composabl_core.agent.skill.skill_controller import SkillController


class ControllerExpertDict(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """

    def __init__(self, *args, **kwargs):
        self.wrong_action_probability = 0.05

    async def compute_action(self, transformed_sensors: Dict, action):
        action = 1 if random.random() < self.wrong_action_probability else 0

        return {
            "increment": action,  # 0 = increment, 1 is decrement
            "increment_box": np.array([-1.5], dtype=np.float32),
            "nested_action": {
                "increment_nested": action,
                "increment_nested_box": np.array([0.0], dtype=np.float32),
            },
        }

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerExpertBox(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """

    def __init__(self, *args, **kwargs):
        self.wrong_action_probability = 0.05

    async def compute_action(self, transformed_sensors: Dict, action):
        return np.array([0.8], dtype=np.float32)

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerSelector(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """

    def __init__(self, *args, **kwargs):
        self.wrong_action_probability = 0.05

    async def compute_action(self, transformed_sensors: Dict, action):
        return 0

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerExpertTuple(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """

    def __init__(self, *args, **kwargs):
        self.wrong_action_probability = 0.05

    async def compute_action(self, transformed_sensors: Dict, action):
        return (
            1,
            np.array([0.5], dtype=np.float32),
            (1, np.array([0.15], dtype=np.float32)),
        )

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerExpertDiscrete(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """

    def __init__(self, *args, **kwargs):
        self.wrong_action_probability = 0.05

    async def compute_action(self, transformed_sensors: Dict, action):
        return 1

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerExpertMultiDiscrete(SkillController):
    """
    The strategy of this controller is to almost always take the correct action. X% of the time
    it will still take a counter action (hallucination)
    """

    def __init__(self, *args, **kwargs):
        self.wrong_action_probability = 0.05

    async def compute_action(self, transformed_sensors: Dict, action):
        return [1, 0]

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerRandomDict(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        return {
            "increment": random.randint(0, 1),  # 0 = increment, 1 is decrement
            "increment_box": np.array([-1.5], dtype=np.float32),
            "nested_action": {
                "increment_nested": random.randint(
                    0, 1
                ),  # 0 = increment, 1 is decrement,
                "increment_nested_box": np.array([0.0], dtype=np.float32),
            },
        }

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerRandomBox(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        return np.array(
            [random.random()], dtype=np.float32
        )  # 0 = increment, 1 is decrement

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerRandomDiscrete(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        return random.randint(0, 1)  # 0 = increment, 1 is decrement

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerRandomTuple(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        return (
            random.randint(0, 1),
            np.array([0.5], dtype=np.float32),
            (random.randint(0, 1), np.array([0.2], dtype=np.float32)),
        )

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerRandomMultiDiscrete(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        return [random.randint(0, 1), 0]  # 0 = increment, 1 is decrement

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerPassThrough(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        set_point = transformed_sensors["teacher-skill-custom-action-space"]
        return float(set_point)

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["teacher-skill-custom-action-space", "counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10


class ControllerDummy(SkillController):
    """
    The strategy of this controller is to take a random action each time
    """

    def __init__(self, *args, **kwargs):
        pass

    async def compute_action(self, transformed_sensors: Dict, action):
        return float(5.0)

    async def transform_sensors(self, sensors):
        return sensors

    async def filtered_sensor_space(self):
        return ["counter"]

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] >= 10

    async def compute_termination(self, transformed_sensors: Dict, action):
        return transformed_sensors["counter"][0] <= -10
