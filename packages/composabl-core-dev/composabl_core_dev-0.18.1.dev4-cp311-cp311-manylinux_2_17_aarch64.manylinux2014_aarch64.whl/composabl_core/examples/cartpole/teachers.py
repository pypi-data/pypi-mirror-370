# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Dict

from composabl_core import CoordinatedGoal, MaintainGoal


class CartpoleTeacher(CoordinatedGoal):
    def __init__(self):
        pole_goal = MaintainGoal(
            "pole_theta", "Maintain pole to upright", target=0, stop_distance=0.418
        )
        cart_goal = MaintainGoal(
            "cart_pos", "Maintain cart to center", target=0, stop_distance=2.4
        )
        super().__init__([pole_goal, cart_goal])

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        # Cartpole might not use an action mask, so this can return None
        return None

    async def transform_sensors(self, sensors, action):
        # For Cartpole, might just return sensors directly
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        # No transformation needed for discrete action space
        return action


class PoleBalanceTeacher(CartpoleTeacher):
    async def compute_reward(self, transformed_sensors: Dict, action, sim_reward):
        pole_angle = abs(transformed_sensors["pole_theta"])
        pole_velocity = abs(transformed_sensors["pole_alpha"])

        # Higher reward for smaller angles and velocities
        return 1.0 - (pole_angle + pole_velocity) / 0.418

    async def compute_termination(self, transformed_sensors: Dict, action):
        """
        For balancing the pole, we terminate early if the pole falls too much
        """
        return abs(transformed_sensors["pole_theta"]) > 0.418

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        """
        For balancing the pole, we consider the pole upright if it's within 3 degrees of vertical
        """
        return abs(transformed_sensors["pole_theta"]) < 0.05  # Less than ~3 degrees


class CartMoveToCenterTeacher(CartpoleTeacher):
    async def compute_reward(self, transformed_sensors: Dict, action, sim_reward):
        cart_position = abs(transformed_sensors["cart_pos"])

        # Reward inversely proportional to distance from center
        return 1.0 - cart_position / 2.4

    async def compute_termination(self, transformed_sensors: Dict, action):
        """
        For moving to center, we terminate early if it's too far from the center
        """
        return abs(transformed_sensors["cart_pos"]) > 2.4

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        """
        For moving to center, we consider the cart at the center if it's within 0.1 units
        """
        return abs(transformed_sensors["cart_pos"]) < 0.1


class BalanceTeacher(MaintainGoal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "pole_theta", "Maintain pole to upright", target=0, stop_distance=0.418
        )

        # defaults the BL and BR

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        # Cartpole might not use an action mask, so this can return None
        return None

    async def transform_sensors(self, sensors, action):
        # For Cartpole, might just return sensors directly
        return sensors

    async def transform_action(self, transformed_sensors: Dict, action):
        # No transformation needed for discrete action space
        return action

    async def filtered_sensor_space(self):
        # Return relevant sensors
        return ["cart_pos", "cart_vel", "pole_theta", "pole_alpha"]
