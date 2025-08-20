# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
import os
import gymnasium.spaces as spaces
from composabl_core.agent.scenario.scenario import Scenario
from composabl_core.agent.skill.skill import Skill
from composabl_core.agent.skill.skill_selector import SkillSelector
from composabl_core.examples.demo.agent import scenarios
from composabl_core.examples.demo.agent.controller import (
    ControllerExpertBox,
    ControllerExpertDict,
    ControllerExpertDiscrete,
    ControllerExpertMultiDiscrete,
    ControllerExpertTuple,
    ControllerRandomBox,
    ControllerRandomDict,
    ControllerRandomDiscrete,
    ControllerRandomMultiDiscrete,
    ControllerRandomTuple,
    ControllerPassThrough,
    ControllerSelector,
    ControllerDummy,
)
from composabl_core.examples.demo.agent.teacher import (
    Teacher,
    TeacherSpaceBox,
    TeacherSpaceDictionary,
    TeacherSpaceDiscrete,
    TeacherSpaceMultiBinary,
    TeacherSpaceMultiDiscrete,
    TeacherSpaceTuple,
    TeacherSpaceText,
    SelectorTeacher,
)

expert_skill_controller_box = Skill("expert-controller", ControllerExpertBox)
random_skill_controller_box = Skill("random-controller", ControllerRandomBox)
selector_sill_controller_box = Skill("selector-controller", ControllerSelector)
pass_through_skill_controller = Skill("pass-through-controller", ControllerPassThrough)
dummy_skill_controller = Skill("pass-through-controller", ControllerDummy)

expert_skill_controller_discrete = Skill("expert-controller", ControllerExpertDiscrete)
random_skill_controller_discrete = Skill("random-controller", ControllerRandomDiscrete)

expert_skill_controller_multi_discrete = Skill(
    "expert-controller", ControllerExpertMultiDiscrete
)
random_skill_controller_multi_discrete = Skill(
    "random-controller", ControllerRandomMultiDiscrete
)

expert_skill_controller_dict = Skill("expert-controller", ControllerExpertDict)
random_skill_controller_dict = Skill("random-controller", ControllerRandomDict)

expert_skill_controller_tuple = Skill("expert-controller", ControllerExpertTuple)
random_skill_controller_tuple = Skill("random-controller", ControllerRandomTuple)

target_skill_nested_scenario = Skill("teacher-skill-nested-scenario", Teacher)
target_skill_box = Skill("teacher-skill-box", TeacherSpaceBox)
target_skill_discrete = Skill("teacher-skill-discrete", TeacherSpaceDiscrete)
target_skill_multi_discrete = Skill(
    "teacher-skill-multidiscrete", TeacherSpaceMultiDiscrete
)
target_skill_multi_binary = Skill("teacher-skill-multibinary", TeacherSpaceMultiBinary)
target_skill_dictionary = Skill("teacher-skill-dictionary", TeacherSpaceDictionary)
target_skill_remote = Skill.from_json(
    {
        "name": "my-remote-dict-teacher",
        "type": "SkillTeacher",
        "config": {
            "remote_address": "http://localhost:8080/cstr-drl-py-0.0.1.tar.gz",
        },
    }
)

# used to test resume training with scenarios
target_skill_dictionary.add_scenario({"test": {"data": "test", "type": "is_equal"}})

target_skill_tuple = Skill("teacher-skill-tuple", TeacherSpaceTuple)
target_skill_text = Skill("teacher-skill-text", TeacherSpaceText)
target_skill_custom_action_space = Skill(
    "teacher-skill-custom-action-space",
    TeacherSpaceDiscrete,
    custom_action_space=spaces.Discrete(2),
)

target_skills = [
    target_skill_nested_scenario,
    target_skill_box,
    target_skill_discrete,
    target_skill_multi_discrete,
    target_skill_multi_binary,
    target_skill_dictionary,
    target_skill_tuple,
    target_skill_custom_action_space,
    target_skill_text,
]

for ts in target_skills:
    for scenario_dict in scenarios:
        ts.add_scenario(Scenario(scenario_dict))

target_skill_nested_scenario.add_scenario(
    {"test": {"data": "test", "type": "is_equal"}}
)

skills_for_space = {
    "box": target_skill_box,
    "discrete": target_skill_discrete,
    "multidiscrete": target_skill_multi_discrete,
    "multibinary": target_skill_multi_binary,
    "dictionary": target_skill_dictionary,
    "tuple": target_skill_tuple,
    "set_point": target_skill_custom_action_space,
    "text": target_skill_text,
}

selector_skill = SkillSelector("skill-selector", SelectorTeacher)
