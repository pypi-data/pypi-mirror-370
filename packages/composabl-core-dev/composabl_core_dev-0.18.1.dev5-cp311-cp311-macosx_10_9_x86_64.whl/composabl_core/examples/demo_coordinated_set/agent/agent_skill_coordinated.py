# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core import Agent
from composabl_core.examples.demo_coordinated_set.agent import coordinated_skill, sensors

agent = Agent()
agent.add_sensors(sensors)
agent.add_coordinated_skill(coordinated_skill)
