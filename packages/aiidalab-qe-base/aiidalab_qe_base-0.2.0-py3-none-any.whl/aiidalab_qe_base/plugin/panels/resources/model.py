import traitlets as tl

from aiidalab_qe_base.models import CodeModel
from aiidalab_qe_base.panels.resources import ResourceSettingsModel


class PluginResourceSettingsModel(ResourceSettingsModel):
    """Base model for plugin resource setting models."""

    dependencies = [
        "global.global_codes",
    ]

    override = tl.Bool(False)

    def add_model(self, identifier: str, model: CodeModel):
        super().add_model(identifier, model)
        model.activate()

    def update(self):
        """Updates the code models from the global resources.

        Skips synchronization with global resources if the user has chosen to override
        the resources for the plugin codes.
        """
        if self.override:
            return
        for _, code_model in self.get_models():
            model_key = code_model.default_calc_job_plugin.replace(".", "__")
            if model_key in self.global_codes:
                code_resources: dict = self.global_codes[model_key]  # type: ignore
                code_model.set_model_state(code_resources)

    def get_model_state(self):
        return {
            "override": self.override,
            **super().get_model_state(),
        }

    def set_model_state(self, parameters: dict):
        self.override = parameters.get("override", False)
        super().set_model_state(parameters)

    def _link_model(self, model: CodeModel):
        tl.link(
            (self, "override"),
            (model, "override"),
        )
