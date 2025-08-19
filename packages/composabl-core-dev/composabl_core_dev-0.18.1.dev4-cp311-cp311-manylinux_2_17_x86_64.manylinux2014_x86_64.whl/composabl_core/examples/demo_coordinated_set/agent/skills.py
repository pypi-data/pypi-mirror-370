# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core import Skill, SkillCoordinatedSet, Scenario

from composabl_core.examples.demo_coordinated_set.agent import scenarios
from composabl_core.examples.demo_coordinated_set.agent.coach import CoordinatedCoach
from composabl_core.examples.demo_coordinated_set.agent.teacher import IncrementTeacher

increment_skill1 = Skill("skill1", IncrementTeacher)
increment_skill2 = Skill("skill2", IncrementTeacher)

coordinated_skill = SkillCoordinatedSet("coordinated_skill", CoordinatedCoach)
coordinated_skill.add_skill(increment_skill1)
coordinated_skill.add_skill(increment_skill2)

for scenario_dict in scenarios:
    scenario = Scenario(scenario_dict)
    coordinated_skill.add_scenario(scenario)
