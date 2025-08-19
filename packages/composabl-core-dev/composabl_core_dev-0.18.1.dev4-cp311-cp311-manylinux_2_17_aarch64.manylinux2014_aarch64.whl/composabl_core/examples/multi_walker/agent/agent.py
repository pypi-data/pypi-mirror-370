# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.agent import Agent
from composabl_core.agent.skill.skill import Skill
from composabl_core.agent.skill.skill_coordinated import SkillCoordinatedSet

from composabl_core.examples.multi_walker.agent.coach import CoordinatedCoach
from composabl_core.examples.multi_walker.agent.sensors_walker_0 import sensors_walker_0
from composabl_core.examples.multi_walker.agent.sensors_walker_1 import sensors_walker_1
from composabl_core.examples.multi_walker.agent.sensors_walker_2 import sensors_walker_2

from composabl_core.examples.multi_walker.agent.teacher import (
    WalkerTeacher0,
    WalkerTeacher1,
    WalkerTeacher2,
)

coordinated_agent = Agent()
sensors_total = sensors_walker_0 + sensors_walker_1 + sensors_walker_2
coordinated_agent.add_sensors(sensors_total)
walker_1 = Skill("walker_0", WalkerTeacher0)
walker_2 = Skill("walker_1", WalkerTeacher1)
walker_3 = Skill("walker_2", WalkerTeacher2)
coordinated_skill = SkillCoordinatedSet(
    "coordinated_skill", CoordinatedCoach, skills=[walker_1, walker_2, walker_3]
)
coordinated_agent.add_coordinated_skill(coordinated_skill)
