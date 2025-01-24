from typing import Tuple, Iterator, List, Union

from dataclasses import dataclass
from pants.engine.rules import rule, collect_rules
from pants.engine.target import Target, Targets, AllTargets, SourcesField, FilteredTargets
from pants.engine.unions import UnionRule
from pants.python.target_types import PythonLibrary


@dataclass(frozen=True)
class Everything:
    """A wrapper type to return a collection of targets from a rule."""

    targets: Tuple[Target, ...]

    def __iter__(self) -> Iterator[Target]:
        return iter(self.targets)

@rule
async def get_all_targets(
    all_targets: AllTargets,
) -> Everything:
    return Everything(tuple(all_targets))

@dataclass(frozen=True)
class LifecycleRequest:
    pass

@dataclass(frozen=True)
class LifecycleResult:
    messages: List[str]

@rule
async def custom_lint(targets: Targets) -> LifecycleResult:
    python_libs = [t for t in targets if isinstance(t, PythonLibrary)]
    messages = []

    for lib in python_libs:
        # Here we just check if the target has any sources.
        # In a real scenario, you'd implement actual linting logic.
        if lib.sources.snapshot.files:
            messages.append(f"Linting {lib.address} with {len(lib.sources.snapshot.files)} files.")
        else:
            messages.append(f"No files to lint in {lib.address}.")

    return LifecycleResult(messages=messages)


def rules():
    return [*collect_rules(), UnionRule(LifecycleRequest, LifecycleResult)]
