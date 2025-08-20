import typing as t

import ipywidgets as ipw
from aiidalab_widgets_base import LoadingWidget

from aiidalab_qe_base.models import CodeModel
from aiidalab_qe_base.widgets import (
    PwCodeResourceSetupWidget,
    QEAppComputationalResourcesWidget,
)

from ..settings import SettingsPanel
from .model import ResourceSettingsModel

RSM = t.TypeVar("RSM", bound=ResourceSettingsModel)


class ResourceSettingsPanel(SettingsPanel[RSM]):
    """Base class for resource setting panels."""

    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.code_widgets: dict[str, QEAppComputationalResourcesWidget] = {}
        self.code_widgets_container = ipw.VBox()

    def register_code_trait_callbacks(self, code_model: CodeModel):
        """Registers event handlers on code model traits."""
        if code_model.default_calc_job_plugin == "quantumespresso.pw":
            code_model.observe(
                self._on_code_resource_change,
                [
                    "parallelization_override",
                    "npool",
                ],
            )
        code_model.observe(
            self._on_code_resource_change,
            [
                "selected",
                "num_cpus",
                "num_nodes",
                "ntasks_per_node",
                "cpus_per_task",
                "max_wallclock_seconds",
            ],
        )

    def _on_code_resource_change(self, _):
        pass

    def _on_code_options_change(self, change: dict):
        widget: ipw.Dropdown = change["owner"]
        widget.disabled = not widget.options

    def _toggle_code(self, code_model: CodeModel):
        if not self.rendered:
            return
        if not code_model.is_rendered:
            loading_message = LoadingWidget(f"Loading {code_model.name} code")
            self.code_widgets_container.children += (loading_message,)
        if code_model.name not in self.code_widgets:
            code_widget = code_model.code_widget_class(
                description=code_model.description,
                default_calc_job_plugin=code_model.default_calc_job_plugin,
            )
            self.code_widgets[code_model.name] = code_widget
        else:
            code_widget = self.code_widgets[code_model.name]
        if not code_model.is_rendered:
            code_widget.observe(
                code_widget.update_resources,
                "value",
            )
            self._render_code_widget(code_model, code_widget)

    def _render_code_widget(
        self,
        code_model: CodeModel,
        code_widget: QEAppComputationalResourcesWidget,
    ):
        ipw.dlink(
            (code_model, "options"),
            (code_widget.code_selection.code_select_dropdown, "options"),
        )
        ipw.link(
            (code_model, "warning"),
            (code_widget.code_selection.output, "value"),
        )
        ipw.link(
            (code_model, "selected"),
            (code_widget, "value"),
        )
        ipw.link(
            (code_model, "num_cpus"),
            (code_widget.num_cpus, "value"),
        )
        ipw.link(
            (code_model, "num_nodes"),
            (code_widget.num_nodes, "value"),
        )
        ipw.link(
            (code_model, "ntasks_per_node"),
            (code_widget.resource_detail.ntasks_per_node, "value"),
        )
        ipw.link(
            (code_model, "cpus_per_task"),
            (code_widget.resource_detail.cpus_per_task, "value"),
        )
        ipw.link(
            (code_model, "max_wallclock_seconds"),
            (code_widget.resource_detail.max_wallclock_seconds, "value"),
        )
        if isinstance(code_widget, PwCodeResourceSetupWidget):
            ipw.link(
                (code_model, "parallelization_override"),
                (code_widget.parallelization.override, "value"),
            )
            ipw.link(
                (code_model, "npool"),
                (code_widget.parallelization.npool, "value"),
            )
        code_widget.code_selection.code_select_dropdown.observe(
            self._on_code_options_change,
            "options",
        )
        code_widgets = self.code_widgets_container.children[:-1]  # type: ignore
        self.code_widgets_container.children = [*code_widgets, code_widget]
        code_model.is_rendered = True
