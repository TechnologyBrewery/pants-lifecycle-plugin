from pants.engine.rules import goal_rule, collect_rules
from pants.engine.goal import Goal, GoalSubsystem
from pants.core.goals.test import run_tests
from pants.core.goals.lint import lint
from pants_uv_lifecycle_plugin.run_uv_sync import run_uv_sync_on_pyproject_modules
from pants_uv_lifecycle_plugin.run_uv_build import run_uv_build_on_pyproject_modules
from pants_uv_lifecycle_plugin.uv_run_behave import uv_run_behave_on_pyproject_modules
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
async def run_lifecycle() -> LifecycleGoal:

    logger.info("`lifecycle` starting!")

    # Run lint
    lint_result = await lint()
    if lint_result.exit_code != 0:
        logger.info("lint failed.")
        return LifecycleGoal(exit_code=lint_result.exit_code)
    
    # Run test
    test_result = await run_tests()
    if test_result.exit_code != 0:
        logger.info("test failed.")
        return LifecycleGoal(exit_code=test_result.exit_code)

    # Run uv-sync
    sync_goal = await run_uv_sync_on_pyproject_modules() #Get(Goal, GoalSubsystem, UvSyncSubsystem)
    if sync_goal.exit_code != 0:
        logger.info("uv-sync failed.")
        return LifecycleGoal(exit_code=sync_goal.exit_code)

    # Run uv-build
    sync_goal = await run_uv_build_on_pyproject_modules() #Get(Goal, GoalSubsystem, UvSyncSubsystem)
    if sync_goal.exit_code != 0:
        logger.info("uv-build failed.")
        return LifecycleGoal(exit_code=sync_goal.exit_code)

    # Run uv-run-behave
    sync_goal = await uv_run_behave_on_pyproject_modules() #Get(Goal, GoalSubsystem, UvSyncSubsystem)
    if sync_goal.exit_code != 0:
        logger.info("uv-run-behave failed.")
        return LifecycleGoal(exit_code=sync_goal.exit_code)

    # If we get here, all steps succeeded.
    logger.info("Lifecycle goal completed successfully.")
    return LifecycleGoal(exit_code=0)

def rules():
    return collect_rules()