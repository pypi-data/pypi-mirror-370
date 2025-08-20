import traitlets as tl

from aiidalab_qe_base.mixins import HasBlockers
from aiidalab_qe_base.panels.panel import PanelModel


class SettingsModel(PanelModel, HasBlockers):
    """Base model for settings models."""

    title = "Settings"
    identifier = "settings"

    include = tl.Bool(False)
    loaded_from_process = tl.Bool(False)

    def update(self):
        """Updates the model."""
        pass

    def get_model_state(self) -> dict:
        """Retrieves the current state of the model as a dictionary."""
        raise NotImplementedError()

    def set_model_state(self, parameters: dict):
        """Distributes the parameters of a loaded calculation to the model."""
        raise NotImplementedError()

    def reset(self):
        """Resets the model to present defaults."""
        pass
