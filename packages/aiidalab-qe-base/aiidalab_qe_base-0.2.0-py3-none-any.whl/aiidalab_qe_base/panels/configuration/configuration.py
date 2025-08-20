import os
import typing as t

from aiidalab_qe_base.mixins import HasInputStructure

from ..settings import SettingsPanel
from .model import ConfigurationSettingsModel

CSM = t.TypeVar("CSM", bound=ConfigurationSettingsModel)


class ConfigurationSettingsPanel(SettingsPanel[CSM]):
    """Base class for configuration settings panels."""

    def refresh(self, specific=""):
        """Refreshes the settings panel.

        Unlinks the panel's widgets. If the panel's model is included in the
        calculation, also updates the model's defaults. Resets the model to
        these defaults if there is no input structure.

        Parameters
        ----------
        `specific` : `str`, optional
            If provided, specifies the level of refresh.
        """
        self.updated = False
        self._unsubscribe()
        if self._model.include:
            self.update(specific)
        if "PYTEST_CURRENT_TEST" in os.environ:
            # Skip resetting to avoid having to inject a structure when testing
            return
        if isinstance(self._model, HasInputStructure) and not self._model.has_structure:
            self._reset()

    def update(self, specific=""):
        """Updates the model if not yet updated.

        Parameters
        ----------
        `specific` : `str`, optional
            If provided, specifies the level of update.
        """
        if self.updated:
            return
        if not self._model.loaded_from_process:
            self._model.update(specific)
        self.updated = True

    def _unsubscribe(self):
        """Unlinks any linked widgets."""
        for link in self.links:
            link.unlink()
        self.links.clear()

    def _reset(self):
        """Resets the model to present defaults."""
        self.updated = False
        self._model.reset()
