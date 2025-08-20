from __future__ import annotations

import traitlets as tl
from aiida import orm
from aiida.common.extendeddicts import AttributeDict

from aiidalab_qe_base.mixins import HasProcess

from ..settings import SettingsModel


class ResultsModel(SettingsModel, HasProcess):
    """Base model for results models."""

    title = "Results"
    identifier = "results"

    process_status_notification = tl.Unicode("")

    _this_process_label = ""
    _this_process_uuid = None

    auto_render = False
    _completed_process = False

    CSS_MAP = {
        "finished": "success",
        "failed": "danger",
        "excepted": "danger",
        "killed": "danger",
        "queued": "warning",
        "running": "info",
        "created": "info",
    }

    @property
    def include(self):
        return self.identifier in self.properties

    @property
    def has_results(self):
        node = self.fetch_child_process_node()
        return node and node.is_finished_ok

    def update(self):
        self.auto_render = self.has_results

    def update_process_status_notification(self):
        if self._completed_process:
            self.process_status_notification = ""
            return
        status = self._get_child_process_status()
        self.process_status_notification = status
        if "success" in status:
            self._completed_process = True

    def fetch_child_process_node(self, which="this") -> orm.ProcessNode | None:
        if not self.process_uuid:
            return
        which = which.lower()
        uuid = getattr(self, f"_{which}_process_uuid")
        label = getattr(self, f"_{which}_process_label")
        if not uuid:
            root = self.fetch_process_node()
            child = next((c for c in root.called if c.process_label == label), None)
            uuid = child.uuid if child else None
        return orm.load_node(uuid) if uuid else None  # type: ignore

    def save_state(self):
        """Saves the current state of the model to the AiiDA database."""
        node = self.fetch_process_node()
        results = node.base.extras.get("results", {})
        results[self.identifier] = self.get_model_state()
        node.base.extras.set("results", results)

    def load_state(self):
        """Loads the state of the model from the AiiDA database."""
        node = self.fetch_process_node()
        results = node.base.extras.get("results", {})
        if self.identifier in results:
            self.set_model_state(results[self.identifier])

    def _get_child_process_status(self, which="this"):
        state, exit_message = self._get_child_state_and_exit_message(which)
        if state == "waiting":
            state = "running"
        status = state.upper()
        if exit_message:
            status = f"{status} ({exit_message})"
        label = "Status" if which == "this" else f"{which.capitalize()} status"
        alert_class = f"alert-{self.CSS_MAP.get(state, 'info')}"
        return f"""
            <div class="alert {alert_class}" style="padding: 5px 10px;">
                <b>{label}:</b> {status}
            </div>
        """

    def _get_child_state_and_exit_message(self, which="this"):
        if not (
            (node := self.fetch_child_process_node(which))
            and hasattr(node, "process_state")
            and node.process_state
        ):
            return "queued", None
        if node.is_failed:
            return "failed", node.exit_message
        return node.process_state.value, None

    def _get_child_outputs(self, which="this"):
        if not (node := self.fetch_child_process_node(which)):
            outputs = super().outputs
            child = which if which != "this" else self.identifier
            return getattr(outputs, child) if child in outputs else AttributeDict({})
        return AttributeDict({key: getattr(node.outputs, key) for key in node.outputs})
