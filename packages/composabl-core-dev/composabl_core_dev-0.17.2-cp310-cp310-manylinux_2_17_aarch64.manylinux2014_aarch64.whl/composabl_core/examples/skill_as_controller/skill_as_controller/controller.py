# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential


from composabl_core import SkillController, Agent
from composabl_train import Trainer


class WeightController2(SkillController):
    def __init__(self, *args, **kwargs):
        config = {
            "license": "",
            "target": {"local": {"address": "localhost:1337"}},
            "env": {
                "name": "composabl",
            },
        }
        self.packaged_skill = None
        trainer = Trainer(config)
        agent = Agent.load("agent.json")

        # get the skill from skill.txt
        with open("skill.txt", "r") as f:
            skill_name = f.read()

        self.packaged_skill = trainer.package(agent, skill=skill_name)

        self.sensors = agent.get_sensors()
        self.obs = None

    async def compute_action(self, obs, action):
        return self.packaged_skill.execute(self.obs)

    async def transform_sensors(self, obs):
        self.obs = obs
        return obs

    async def filtered_sensor_space(self):
        return self.sensors

    async def compute_success_criteria(self, transformed_obs, action):
        return False

    async def compute_termination(self, transformed_obs, action):
        return False
