# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Dict

from composabl_core.agent.skill.skill_coach import SkillCoach


class CoordinatedCoach(SkillCoach):
    def __init__(self, *args, **kwargs):
        pass

    async def compute_reward(self, multi_obs, multi_action, multi_reward):
        """
        Computes the reward for the given transformed sensors and action
        :param multi_obs: Dict - The transformed sensors from all the agents
        :param multi_action: Dict - The actions from all the agents
        :param multi_reward: Dict - The rewards from all the agents

        :return: The total reward for the coach
        """
        return 0

    async def compute_action_mask(self, transformed_sensors: Dict, action):
        pass

    async def compute_success_criteria(self, transformed_sensors: Dict, action):
        return False

    async def compute_termination(self, transformed_sensors: Dict, action):
        return False

    async def transform_action(self, composabl_obs, action):
        return action
