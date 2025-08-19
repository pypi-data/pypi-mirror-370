# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core import SkillCoordinatedPopulation, SkillPopulation, Scenario

from composabl_core.examples.demo_coordinated_set.agent import scenarios
from composabl_core.examples.demo_coordinated_set.agent.coach import CoordinatedCoach
from composabl_core.examples.demo_coordinated_set.agent.teacher import IncrementTeacher

population_1 = SkillPopulation("car", IncrementTeacher, amount=2)
population_2 = SkillPopulation("plane", IncrementTeacher, amount=3)
coordinated_skill = SkillCoordinatedPopulation("my-awesome-coordinated-population", CoordinatedCoach)
coordinated_skill.add_population(population_1)
coordinated_skill.add_population(population_2)

for scenario_dict in scenarios:
    scenario = Scenario(scenario_dict)
    coordinated_skill.add_scenario(scenario)
