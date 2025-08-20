import typing as t

import ipywidgets as ipw

from aiidalab_qe_base.models import CodeModel
from aiidalab_qe_base.panels.resources import ResourceSettingsPanel
from aiidalab_qe_base import widgets

from .model import PluginResourceSettingsModel

PRSM = t.TypeVar("PRSM", bound=PluginResourceSettingsModel)


class PluginResourceSettingsPanel(ResourceSettingsPanel[PRSM]):
    """Base class for plugin resource setting panels."""

    def __init__(self, model: PRSM, **kwargs):
        super().__init__(model, **kwargs)

        self._model.observe(
            self._on_global_codes_change,
            "global_codes",
        )
        self._model.observe(
            self._on_override_change,
            "override",
        )

    def render(self):
        if self.rendered:
            return

        self.override_help = ipw.HTML(
            "Click to override the resource settings for this plugin."
        )
        self.override = ipw.Checkbox(
            description="",
            indent=False,
            layout=ipw.Layout(max_width="3%"),
        )
        ipw.link(
            (self._model, "override"),
            (self.override, "value"),
        )

        self.children = [
            ipw.HBox(
                children=[
                    self.override,
                    self.override_help,
                ]
            ),
            self.code_widgets_container,
        ]

        self.rendered = True

        # Render any active codes
        for _, code_model in self._model.get_models():
            if code_model.is_active:
                self._toggle_code(code_model)

    def _on_global_codes_change(self, _):
        self._model.update()

    def _on_override_change(self, _):
        self._model.update()

    def _render_code_widget(
        self,
        code_model: CodeModel,
        code_widget: widgets.QEAppComputationalResourcesWidget,
    ):
        super()._render_code_widget(code_model, code_widget)
        self._link_override_to_widget_disable(code_model, code_widget)

    def _link_override_to_widget_disable(
        self,
        code_model: CodeModel,
        code_widget: widgets.QEAppComputationalResourcesWidget,
    ):
        """Links the override attribute of the code model to the disable attribute
        of subwidgets of the code widget."""
        ipw.dlink(
            (code_model, "override"),
            (code_widget.code_selection.code_select_dropdown, "disabled"),
            lambda override: not override,
        )
        ipw.dlink(
            (code_model, "override"),
            (code_widget.num_cpus, "disabled"),
            lambda override: not override,
        )
        ipw.dlink(
            (code_model, "override"),
            (code_widget.num_nodes, "disabled"),
            lambda override: not override,
        )
        ipw.dlink(
            (code_model, "override"),
            (code_widget.btn_setup_resource_detail, "disabled"),
            lambda override: not override,
        )
        if isinstance(code_widget, widgets.PwCodeResourceSetupWidget):
            ipw.dlink(
                (code_model, "override"),
                (code_widget.parallelization.override, "disabled"),
                lambda override: not override,
            )
            ipw.dlink(
                (code_model, "override"),
                (code_widget.parallelization.npool, "disabled"),
                lambda override: not override,
            )
