import typing as t

import ipywidgets as ipw

from aiidalab_qe_base.widgets import InAppGuide

from ..panel import Panel
from .model import ResultsModel

RM = t.TypeVar("RM", bound=ResultsModel)


class ResultsPanel(Panel[RM]):
    """Base class for all the result panels.

    The base class has a method to load the result of the calculation.
    And a show method to display it in the panel.
    It has a update method to update the result in the panel.
    """

    _loading_message = "Loading {identifier} results"

    def __init__(self, model: RM, **kwargs):
        super().__init__(model=model, **kwargs)
        self._model.observe(
            self._on_process_change,
            "process_uuid",
        )
        self._model.observe(
            self._on_monitor_counter_change,
            "monitor_counter",
        )

    def render(self):
        if self.rendered:
            if self._model.identifier == "structure":
                self._render()
            return

        if not self._model.has_process:
            return

        self.guide = InAppGuide(
            identifier=f"{self._model.identifier}-results",
            classes=["results-panel-guide"],
        )
        self.save_state_button = ipw.Button(
            description="Save state",
            tooltip="Save the current visualization settings",
            button_style="primary",
            icon="save",
        )
        self.save_state_button.on_click(self._save_state)
        self.load_state_button = ipw.Button(
            description="Load state",
            tooltip="Load previously saved visualization settings",
            button_style="primary",
            icon="download",
        )
        self.load_state_button.on_click(self._load_state)
        self.state_buttons = ipw.HBox(
            children=[self.save_state_button, self.load_state_button],
        )

        self.results_container = ipw.VBox()

        if self._model.auto_render:
            self.children = [
                self.guide,
                self.results_container,
            ]
            self._load_results()
        else:
            children = [self.guide]
            if (
                self._model.identifier != "structure"
                or "relax" in self._model.properties
            ):
                children.append(self._get_controls_section())
            children.append(self.results_container)
            self.children = children
            if self._model.identifier == "structure":
                self._load_results()

        self.rendered = True

    def _on_process_change(self, _):
        self._model.update()

    def _on_monitor_counter_change(self, _):
        self._model.update_process_status_notification()

    def _on_load_results_click(self, _):
        self.load_controls.children = []
        self._load_results()

    def _load_results(self):
        self.results_container.children = [self.loading_message]
        self._render()
        self._post_render()

    def _get_controls_section(self) -> ipw.VBox:
        self.process_status_notification = ipw.HTML()
        ipw.dlink(
            (self._model, "process_status_notification"),
            (self.process_status_notification, "value"),
        )

        self.load_results_button = ipw.Button(
            description="Load results",
            button_style="warning",
            tooltip="Load the results",
            icon="refresh",
        )
        ipw.dlink(
            (self._model, "monitor_counter"),
            (self.load_results_button, "disabled"),
            lambda _: not self._model.has_results,
        )
        self.load_results_button.on_click(self._on_load_results_click)

        self.load_controls = ipw.HBox(
            children=[]
            if self._model.auto_render or self._model.identifier == "structure"
            else [
                self.load_results_button,
                ipw.HTML("""
                    <div style="margin-left: 10px">
                        <b>Note:</b> Load time may vary depending on the size of the
                        calculation
                    </div>
                """),
            ]
        )

        return ipw.VBox(
            children=[
                self.process_status_notification,
                self.load_controls,
            ]
        )

    def _render(self):
        raise NotImplementedError()

    def _post_render(self):
        pass

    def _save_state(self, _=None):
        """Save the current state of the results panel."""
        self._model.save_state()

    def _load_state(self, _=None):
        """Load a previously saved state of the results panel."""
        self._model.load_state()
