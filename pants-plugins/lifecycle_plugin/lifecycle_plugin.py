from typing import List

from dataclasses import dataclass
from pants.engine.rules import Get, MultiGet, goal_rule, collect_rules
from pants.engine.goal import Goal, GoalSubsystem
from pants.engine.target import Target, Targets, AllTargets, SourcesField, FilteredTargets
from pants.core.goals.test import TestResult
from pants.core.goals.lint import LintTargetsRequest, LintResult
from lifecycle_plugin.lifecycle_rules import Everything, LifecycleRequest, LifecycleResult

import logging


logger = logging.getLogger("lifecycle_plugin")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


class LifecycleSubsystem(GoalSubsystem):
    name = "lifecycle"
    help = "Runs a series of plugins to ease understanding needed to build your project."


class LifecycleGoal(Goal):
    subsystem_cls = LifecycleSubsystem
    environment_behavior = Goal.EnvironmentBehavior.LOCAL_ONLY


@goal_rule(desc="run lifecycle")
async def run_lifecycle(
        source_targets: Everything
) -> LifecycleGoal:

    logger.info("`lifecycle` starting!")
    lint_result, test_result = await MultiGet(
        Get(LintResult, LintTargetsRequest(source_targets)),
        Get(TestResult, Target, source_targets)
    )

    logger.info(f"{lint_result.stdout}\n{test_result.stdout}")

    logger.info("`lifecycle` completed!")

    return LifecycleGoal(exit_code=max(lint_result.exit_code, test_result.exit_code))
    # return LifecycleGoal(0)

def rules():
    return collect_rules()