import sys
import typing as t
from datetime import datetime

import traitlets as tl
from aiida import orm
from dateutil.relativedelta import relativedelta

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class HasTraits(tl.HasTraits):
    """Wrapper on `tl.HasTraits` for improved static type checking."""

    # For IDE type checking
    # Type checking struggles with `traitlets.HasTraits`, which inherits
    # `traitlets.HasDescriptors`, which in turn defines `__new__(...) -> t.Any`
    def __new__(cls, *args: t.Any, **kwargs: t.Any) -> Self:
        return super().__new__(cls, *args, **kwargs)


def set_component_resources(component, code_info):
    """Set the resources for a given component based on the code info."""
    # Ensure code_info is not None or empty
    # ? XXX: from jyu, need to pop a warning to plugin developer or what?
    if code_info:
        code: orm.Code = code_info["code"]
        if code.computer.scheduler_type == "hyperqueue":
            component.metadata.options.resources = {
                "num_cpus": code_info["nodes"]
                * code_info["ntasks_per_node"]
                * code_info["cpus_per_task"]
            }
        else:
            # XXX: jyu should properly deal with None type of scheduler_type which can
            # be "core.direct" (will be replaced by hyperqueue) and "core.slurm" ...
            component.metadata.options.resources = {
                "num_machines": code_info["nodes"],
                "num_mpiprocs_per_machine": code_info["ntasks_per_node"],
                "num_cores_per_mpiproc": code_info["cpus_per_task"],
            }

        max_wallclock_seconds = code_info["max_wallclock_seconds"]
        component.metadata.options["max_wallclock_seconds"] = max_wallclock_seconds

        if "parallelization" in code_info:
            component.parallelization = orm.Dict(dict=code_info["parallelization"])


def enable_pencil_decomposition(component):
    """Enable the pencil decomposition for the given component."""

    component.settings = orm.Dict({"CMDLINE": ["-pd", ".true."]})


def shallow_copy_nested_dict(d):
    """Recursively copies only the dictionary structure but keeps value references."""
    if isinstance(d, dict):
        return {key: shallow_copy_nested_dict(value) for key, value in d.items()}
    return d


def format_time(time: datetime):
    return time.strftime("%Y-%m-%d %H:%M:%S")


def relative_time(time: datetime):
    # TODO consider using humanize or arrow libraries for this
    now = datetime.now(time.tzinfo)
    delta = relativedelta(now, time)
    if delta.years > 0:
        return f"{delta.years} year{'s' if delta.years > 1 else ''} ago"
    elif delta.months > 0:
        return f"{delta.months} month{'s' if delta.months > 1 else ''} ago"
    elif delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.hours > 0:
        return f"{delta.hours} hour{'s' if delta.hours > 1 else ''} ago"
    elif delta.minutes > 0:
        return f"{delta.minutes} minute{'s' if delta.minutes > 1 else ''} ago"
    else:
        return f"{delta.seconds} second{'s' if delta.seconds > 1 else ''} ago"
