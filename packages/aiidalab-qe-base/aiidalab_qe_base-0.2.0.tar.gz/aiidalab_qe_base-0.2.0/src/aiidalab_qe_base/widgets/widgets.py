from __future__ import annotations

from threading import Event, Thread
from time import time

import ipywidgets as ipw
import traitlets as tl
from aiida import orm
from aiida.common.exceptions import NotExistent
from aiidalab_widgets_base import ComputationalResourcesWidget, LoadingWidget
from IPython.display import clear_output, display


class InfoBox(ipw.VBox):
    """The `InfoBox` component is used to provide additional info regarding a widget or an app."""

    def __init__(self, classes: list[str] | None = None, **kwargs):
        """`InfoBox` constructor.

        Parameters
        ----------
        `classes` : `list[str]`, optional
            One or more CSS classes.
        """
        super().__init__(**kwargs)
        self.add_class("info-box")
        for custom_classes in classes or []:
            for custom_class in custom_classes.split(" "):
                if custom_class:
                    self.add_class(custom_class)


class InAppGuide(InfoBox):
    """The `InAppGuide` is used to set up toggleable in-app guides.

    Attributes
    ----------
    `manager` : `GuideManager`
        A local reference to the global guide manager.
    `identifier` : `str`, optional
        If content `children` are not provided directly, the `identifier`
        is used to fetch the corresponding guide section from the guide
        currently loaded by the guide manager.

    Raises
    ------
    `ValueError`
        If neither content `children` or a guide section `identifier` are provided.
    """

    def __init__(
        self,
        children: list | None = None,
        guide_id: str = "",
        identifier: str = "",
        classes: list[str] | None = None,
        **kwargs,
    ):
        """`InAppGuide` constructor.

        Parameters
        ----------
        `children` : `list`, optional
            The content children of this guide section.
        `guide_id` : `str`, optional
            The associated guide id to be used in conjunction with content children.
            If none provided, the widget-based guide section will be shown for all
            guides.
        `identifier` : `str`, optional
            If content `children` are not provided directly, the `identifier`
            is used to fetch the corresponding guide section from the guide
            currently loaded by the guide manager.
        `classes` : `list[str]`, optional
            One or more CSS classes.
        """
        from aiidalab_qe.common.guide_manager import guide_manager

        self.manager = guide_manager

        super().__init__(
            classes=[
                "in-app-guide",
                *(classes or []),
            ],
            **kwargs,
        )

        if children:
            self.guide_id = guide_id
            self.children = children
            self.identifier = None
        elif identifier:
            self.guide_id = None
            self.children = []
            self.identifier = identifier
        else:
            raise ValueError("No widgets or path identifier provided")

        self.manager.observe(
            self._on_active_guide_change,
            "active_guide",
        )

        # This manual toggle call is necessary because the guide
        # may be contained in a component that was not yet rendered
        # when a guide was selected.
        self._on_active_guide_change(None)

    def _on_active_guide_change(self, _):
        self._update_contents()
        self._toggle_guide()

    def _update_contents(self):
        """Update the contents of the guide section."""
        if not self.identifier:
            return
        html = self.manager.get_guide_section_by_id(self.identifier)
        self.children = [ipw.HTML(str(html))] if html else []

    def _toggle_guide(self):
        """Toggle the visibility of the guide section."""
        self.layout.display = (
            "flex"
            if self.children
            and (
                # file-based guide section
                (self.identifier and self.manager.has_guide)
                # widget-based guide section shown for all guides
                or (not self.guide_id and self.manager.has_guide)
                # widget-based guide section shown for a specific guide
                or self.guide_id == self.manager.active_guide
            )
            else "none"
        )


class LinkButton(ipw.HTML):
    disabled = tl.Bool(False)

    def __init__(
        self,
        description=None,
        link="",
        in_place=False,
        class_="",
        style_="",
        icon="",
        tooltip="",
        disabled=False,
        **kwargs,
    ):
        html = f"""
            <a
                role="button"
                href="{link}"
                title="{tooltip or description}"
                target="{"_self" if in_place else "_blank"}"
                style="cursor: default; {style_}"
            >
        """
        if icon:
            html += f"<i class='fa fa-{icon}'></i>"

        html += f"{description}</a>"

        super().__init__(value=html, **kwargs)

        self.add_class("jupyter-button")
        self.add_class("widget-button")
        self.add_class("link-button")
        if class_:
            self.add_class(class_)

        self.disabled = disabled

    @tl.observe("disabled")
    def _on_disabled(self, change):
        if change["new"]:
            self.add_class("disabled")
        else:
            self.remove_class("disabled")


class HBoxWithUnits(ipw.HBox):
    def __init__(self, widget: ipw.ValueWidget, units: str, **kwargs):
        super().__init__(
            children=[
                widget,
                ipw.HTML(units),
            ],
            layout={
                "align_items": "center",
                "grid_gap": "2px",
            }
            | kwargs.pop("layout", {}),
            **kwargs,
        )
        self.add_class("hbox-with-units")


class LazyLoader(ipw.VBox):
    identifier = "widget"

    def __init__(self, widget_class, widget_kwargs=None, **kwargs):
        super().__init__(
            children=[LoadingWidget(f"Loading {self.identifier}")],
            **kwargs,
        )

        self._widget_class = widget_class
        self._widget_kwargs = widget_kwargs or {}

        self.rendered = False

    def set_widget_kwargs(self, kwargs):
        self._widget_kwargs = kwargs

    def render(self):
        if self.rendered:
            return
        self.widget = self._widget_class(**self._widget_kwargs)
        self.children = [self.widget]
        self.rendered = True


class ProgressBar(ipw.HBox):
    class AnimationRate(float):
        pass

    description = tl.Unicode()
    value = tl.Union([tl.Float(), tl.Instance(AnimationRate)])
    bar_style = tl.Unicode()

    _animation_rate = tl.Float()

    def __init__(self, description_layout=None, *args, **kwargs):
        if description_layout is None:
            description_layout = ipw.Layout(width="auto", flex="2 1 auto")

        self._label = ipw.Label(layout=description_layout)
        self._progress_bar = ipw.FloatProgress(
            min=0, max=1.0, layout=ipw.Layout(width="auto", flex="1 1 auto")
        )

        tl.link((self, "description"), (self._label, "value"))
        tl.link((self, "bar_style"), (self._progress_bar, "bar_style"))

        self._animate_stop_event = Event()
        self._animate_thread = None

        super().__init__([self._label, self._progress_bar], *args, **kwargs)

    def _animate(self, refresh_rate=0.01):
        v0 = self._progress_bar.value
        t0 = time()

        while not self._animate_stop_event.wait(refresh_rate):
            self._progress_bar.value = (v0 + (time() - t0) * self._animation_rate) % 1.0

    def _start_animate(self):
        if self._animate_thread is not None:
            raise RuntimeError("Cannot start animation more than once!")

        self._animate_thread = Thread(target=self._animate)
        self._animate_thread.start()

    def _stop_animate(self):
        self._animate_stop_event.set()
        self._animate_thread.join()
        self._animate_stop_event.clear()
        self._animate_thread = None

    @tl.default("_animation_rate")
    def _default_animation_rate(self):
        return 0

    @tl.observe("_animation_rate")
    def _observe_animation_rate(self, change):
        if change["new"] and not change["old"]:
            self._start_animate()
        elif not change["new"] and change["old"]:
            self._stop_animate()

    @tl.validate("value")
    def _validate_value(self, proposal):
        if isinstance(proposal["value"], self.AnimationRate):
            if proposal["value"] < 0:
                raise tl.TraitError("The animation rate must be non-negative.")

        elif not 0 <= proposal["value"] <= 1.0:
            raise tl.TraitError("The value must be between 0 and 1.0.")

        return proposal["value"]

    @tl.observe("value")
    def _observe_value(self, change):
        if isinstance(change["new"], self.AnimationRate):
            self._animation_rate = change["new"]
        else:
            self._animation_rate = 0
            self._progress_bar.value = change["new"]


class QEAppComputationalResourcesWidget(ipw.VBox):
    value = tl.Unicode(allow_none=True)
    nodes = tl.Int(default_value=1)
    cpus = tl.Int(default_value=1)

    def __init__(self, **kwargs):
        """Widget to setup the compute resources, which include the code,
        the number of nodes and the number of cpus.
        """
        self.code_selection = ComputationalResourcesWidget(
            description=kwargs.pop("description", None),
            default_calc_job_plugin=kwargs.pop("default_calc_job_plugin", None),
            include_setup_widget=False,
            fetch_codes=False,
            **kwargs,
        )
        self.code_selection.layout.width = "80%"

        self.num_nodes = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            max=1000,
            description="Nodes",
        )

        self.num_cpus = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            description="CPUs",
        )

        self.btn_setup_resource_detail = ipw.ToggleButton(description="More")
        self.btn_setup_resource_detail.observe(
            self._setup_resource_detail,
            "value",
        )

        self._setup_resource_detail_output = ipw.Output(layout={"width": "500px"})

        # combine code, nodes and cpus
        children = [
            ipw.HBox(
                children=[
                    self.code_selection,
                    self.num_nodes,
                    self.num_cpus,
                    self.btn_setup_resource_detail,
                ]
            ),
            self._setup_resource_detail_output,
        ]
        super().__init__(children=children, **kwargs)

        self.resource_detail = ResourceDetailSettings()

        tl.dlink(
            (self.num_cpus, "value"),
            (self.resource_detail.ntasks_per_node, "value"),
        )

        tl.link((self.code_selection, "value"), (self, "value"))

    def update_resources(self, change):
        if change["new"]:
            try:
                computer = orm.load_code(change["new"]).computer
            except NotExistent:
                computer = None
            self.set_resource_defaults(computer)

    def set_resource_defaults(self, computer=None):
        if computer is None:
            self.num_nodes.disabled = True
            self.num_nodes.value = 1
            self.num_cpus.max = 1
            self.num_cpus.value = 1
            self.num_cpus.description = "CPUs"
        else:
            default_mpiprocs = computer.get_default_mpiprocs_per_machine()
            self.num_nodes.disabled = (
                True if computer.hostname == "localhost" else False
            )
            self.num_cpus.max = default_mpiprocs
            self.num_cpus.value = (
                1 if computer.hostname == "localhost" else default_mpiprocs
            )
            self.num_cpus.description = "CPUs"

    @property
    def parameters(self):
        return self.get_parameters()

    def get_parameters(self):
        """Return the parameters."""
        parameters = {
            "code": self.code_selection.value,
            "nodes": self.num_nodes.value,
            "cpus": self.num_cpus.value,
        }
        parameters.update(self.resource_detail.parameters)
        return parameters

    @parameters.setter
    def parameters(self, parameters):
        self.set_parameters(parameters)

    def set_parameters(self, parameters):
        """Set the parameters."""
        self.code_selection.value = parameters["code"]
        if "nodes" in parameters:
            self.num_nodes.value = parameters["nodes"]
        if "cpus" in parameters:
            self.num_cpus.value = parameters["cpus"]
        if "ntasks_per_node" in parameters:
            self.resource_detail.ntasks_per_node.value = parameters["ntasks_per_node"]
        if "cpus_per_task" in parameters:
            self.resource_detail.cpus_per_task.value = parameters["cpus_per_task"]
        if "max_wallclock_seconds" in parameters:
            self.resource_detail.max_wallclock_seconds.value = parameters[
                "max_wallclock_seconds"
            ]

    def _setup_resource_detail(self, _=None):
        with self._setup_resource_detail_output:
            clear_output()
            if self.btn_setup_resource_detail.value:
                self._setup_resource_detail_output.layout = {
                    "width": "500px",
                    "border": "1px solid gray",
                }

                children = [
                    self.resource_detail,
                ]
                display(*children)
            else:
                self._setup_resource_detail_output.layout = {
                    "width": "500px",
                    "border": "none",
                }


class ResourceDetailSettings(ipw.VBox):
    """Widget for setting the Resource detail."""

    prompt = ipw.HTML(
        """<div style="line-height:120%; padding-top:0px">
        <p style="padding-bottom:10px">
        Specify the parameters for the scheduler (only for advanced user). <br>
        These should be specified accordingly to the computer where the code will run.
        </p></div>"""
    )

    def __init__(self, **kwargs):
        self.ntasks_per_node = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            max=1000,
            description="ntasks-per-node",
            style={"description_width": "100px"},
        )
        self.cpus_per_task = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            description="cpus-per-task",
            style={"description_width": "100px"},
        )
        self.max_wallclock_seconds = ipw.BoundedIntText(
            value=3600 * 12,
            step=3600,
            min=60 * 10,
            max=3600 * 24,
            description="max seconds",
            style={"description_width": "100px"},
        )
        super().__init__(
            children=[
                self.prompt,
                self.ntasks_per_node,
                self.cpus_per_task,
                self.max_wallclock_seconds,
            ],
            **kwargs,
        )

    @property
    def parameters(self):
        return self.get_parameters()

    def get_parameters(self):
        """Return the parameters."""
        return {
            "ntasks_per_node": self.ntasks_per_node.value,
            "cpus_per_task": self.cpus_per_task.value,
            "max_wallclock_seconds": self.max_wallclock_seconds.value,
        }

    @parameters.setter
    def parameters(self, parameters):
        self.ntasks_per_node.value = parameters.get("ntasks_per_node", 1)
        self.cpus_per_task.value = parameters.get("cpus_per_task", 1)
        self.max_wallclock_seconds.value = parameters.get(
            "max_wallclock_seconds", 3600 * 12
        )

    def reset(self):
        """Reset the settings."""
        self.ntasks_per_node.value = 1
        self.cpus_per_task.value = 1
        self.max_wallclock_seconds.value = 3600 * 12


class ParallelizationSettings(ipw.VBox):
    """Widget for setting the parallelization settings."""

    prompt = ipw.HTML(
        """<div style="line-height:120%; padding-top:0px">
        <p style="padding-bottom:10px">
        Specify the number of k-points pools for the pw.x calculations (only for advanced user).
        </p></div>"""
    )

    def __init__(self, **kwargs):
        extra = {
            "style": {"description_width": "150px"},
            "layout": {"min_width": "180px"},
        }
        self.npool = ipw.BoundedIntText(
            value=1,
            step=1,
            min=1,
            max=128,
            description="Number of k-pools",
            **extra,
        )
        self.override = ipw.Checkbox(
            description="",
            indent=False,
            value=False,
            layout=ipw.Layout(max_width="20px"),
        )
        ipw.dlink(
            (self.override, "value"),
            (self.npool.layout, "display"),
            lambda override: "block" if override else "none",
        )

        super().__init__(
            children=[
                ipw.HBox(
                    children=[
                        self.override,
                        self.prompt,
                        self.npool,
                    ],
                    layout=ipw.Layout(justify_content="flex-start"),
                ),
            ],
            **kwargs,
        )

        # set the default visibility of the widget
        self.npool.layout.display = "none"

    def reset(self):
        self.npool.value = 1


class PwCodeResourceSetupWidget(QEAppComputationalResourcesWidget):
    """ComputationalResources Widget for the pw.x calculation."""

    nodes = tl.Int(default_value=1)

    def __init__(self, **kwargs):
        # By definition, npool must be a divisor of the total number of k-points
        # thus we can not set a default value here, or from the computer.
        self.parallelization = ParallelizationSettings()
        super().__init__(**kwargs)
        # add nodes and cpus into the children of the widget
        self.children += (self.parallelization,)

    def get_parallelization(self):
        """Return the parallelization settings."""
        parallelization = (
            {"npool": self.parallelization.npool.value}
            if self.parallelization.override.value
            else {}
        )
        return parallelization

    def set_parallelization(self, parallelization):
        """Set the parallelization settings."""
        if "npool" in parallelization:
            self.parallelization.override.value = True
            self.parallelization.npool.value = parallelization["npool"]

    def get_parameters(self):
        """Return the parameters."""
        parameters = super().get_parameters()
        parameters.update({"parallelization": self.get_parallelization()})
        return parameters

    def set_parameters(self, parameters):
        """Set the parameters."""
        super().set_parameters(parameters)
        if "parallelization" in parameters:
            self.set_parallelization(parameters["parallelization"])
