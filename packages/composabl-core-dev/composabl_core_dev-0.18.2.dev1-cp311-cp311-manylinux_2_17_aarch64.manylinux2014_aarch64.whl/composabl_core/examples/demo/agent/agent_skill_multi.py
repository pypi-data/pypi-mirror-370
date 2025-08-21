# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from composabl_core.agent.agent import Agent
from composabl_core.agent.skill.skill import Skill
from composabl_core.agent.skill.skill_selector import SkillSelector
from composabl_core.examples.demo.agent import (
    expert_skill_controller_box,
    expert_skill_controller_dict,
    expert_skill_controller_discrete,
    expert_skill_controller_multi_discrete,
    expert_skill_controller_tuple,
    random_skill_controller_box,
    random_skill_controller_dict,
    random_skill_controller_discrete,
    random_skill_controller_multi_discrete,
    random_skill_controller_tuple,
    selector_sill_controller_box,
    target_skill_box,
    target_skill_dictionary,
    target_skill_discrete,
    target_skill_multi_discrete,
    target_skill_tuple,
    target_skill_text,
    mapped_sensors_dict,
    sensors_dict,
    selector_skill
)
from composabl_core.examples.demo.agent.teacher import (
    SelectorTeacher
)
from composabl_core.examples.demo.agent.controller import (
    ControllerExpertDict,
    ControllerRandomDict,
)
from composabl_core.examples.demo.agent.teacher import TeacherSpaceDictionary

from copy import deepcopy
agent_dictionary = Agent()
agent_dictionary.add_sensors(mapped_sensors_dict["dictionary"])
agent_dictionary.add_skill(expert_skill_controller_dict)
agent_dictionary.add_skill(random_skill_controller_dict)
agent_dictionary.add_selector_skill(
    selector_skill,
    children=[expert_skill_controller_dict, random_skill_controller_dict],
    fixed_order=True,
    repeat=False,
)

agent_box = Agent()
agent_box.add_sensors(mapped_sensors_dict["box"])
agent_box.add_skill(expert_skill_controller_box)
agent_box.add_skill(random_skill_controller_box)
agent_box.add_selector_skill(
    selector_skill,
    children=[expert_skill_controller_box, random_skill_controller_box],
    fixed_order=True,
    repeat=False,
)

agent_discrete = Agent()
agent_discrete.add_sensors(mapped_sensors_dict["discrete"])
agent_discrete.add_skill(expert_skill_controller_discrete)
agent_discrete.add_skill(random_skill_controller_discrete)
agent_discrete.add_selector_skill(
    selector_skill,
    children=[expert_skill_controller_discrete, random_skill_controller_discrete],
    fixed_order=True,
    repeat=False,
)

agent_multidiscrete = Agent()
agent_multidiscrete.add_sensors(mapped_sensors_dict["multidiscrete"])
agent_multidiscrete.add_skill(expert_skill_controller_multi_discrete)
agent_multidiscrete.add_skill(random_skill_controller_multi_discrete)
agent_multidiscrete.add_selector_skill(
    selector_skill,
    children=[
        expert_skill_controller_multi_discrete,
        random_skill_controller_multi_discrete,
    ],
    fixed_order=True,
    repeat=False,
)


agent_tuple = Agent()
agent_tuple.add_sensors(mapped_sensors_dict["tuple"])
agent_tuple.add_skill(expert_skill_controller_tuple)
agent_tuple.add_skill(random_skill_controller_tuple)
agent_tuple.add_selector_skill(
    selector_skill,
    children=[expert_skill_controller_tuple, random_skill_controller_tuple],
    fixed_order=True,
    repeat=False,
)


controller_agent = Agent()
controller_agent.add_sensors(mapped_sensors_dict["box"])
controller_agent.add_skill(expert_skill_controller_box)
controller_agent.add_skill(random_skill_controller_box)
controller_agent.add_selector_skill(
    selector_skill,
    children=[expert_skill_controller_box, random_skill_controller_box],
    fixed_order=False,
    repeat=True,
)

agent_dictionary_api_context_manager = Agent()

with SkillSelector("target_skill_dictionary", TeacherSpaceDictionary) as ss1:
    with Skill(
        "expert-controller", ControllerExpertDict
    ) as expert_skill_controller_dict:
        ss1.add_child(expert_skill_controller_dict)
        agent_dictionary_api_context_manager.add_skill(expert_skill_controller_dict)

    with Skill(
        "random-controller", ControllerRandomDict
    ) as random_skill_controller_dict:
        ss1.add_child(random_skill_controller_dict)
        agent_dictionary_api_context_manager.add_skill(random_skill_controller_dict)

    agent_dictionary_api_context_manager.add_sensors(mapped_sensors_dict["dictionary"])
    agent_dictionary_api_context_manager.add_selector_skill(
        ss1, fixed_order=True, repeat=False
    )

agent_text = Agent()
agent_text.add_sensors(sensors_dict["text"])
agent_text.add_skill(expert_skill_controller_discrete)
agent_text.add_skill(random_skill_controller_discrete)
agent_text.add_selector_skill(
    selector_skill,
    children=[expert_skill_controller_discrete, random_skill_controller_discrete],
    fixed_order=True,
    repeat=False,
)

agent_drl_child = Agent()
agent_drl_child.add_sensors(mapped_sensors_dict["box"])
agent_drl_child.add_skill(target_skill_box)
agent_drl_child.add_skill(target_skill_box)
agent_drl_child.add_selector_skill(
    SkillSelector("skill-selector-drl-child", SelectorTeacher),
    children=[target_skill_box, target_skill_box],
    fixed_order=False,
    repeat=True,
)


agents_for_space = {
    "box": agent_box,
    "dictionary": agent_dictionary,
    "dictionary_api_context_manager": agent_dictionary_api_context_manager,
    "discrete": agent_discrete,
    "multidiscrete": agent_multidiscrete,
    "tuple": agent_tuple,
    "controller_box": controller_agent,
    "text": agent_text,
    "drl_child": agent_drl_child,
}
