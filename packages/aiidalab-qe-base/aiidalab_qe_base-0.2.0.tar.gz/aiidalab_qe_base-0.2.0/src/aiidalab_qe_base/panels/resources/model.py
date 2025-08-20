import traitlets as tl
from aiida import orm

from aiidalab_qe_base.mixins import HasModels
from aiidalab_qe_base.models import CodeModel

from ..settings import SettingsModel


class ResourceSettingsModel(SettingsModel, HasModels[CodeModel]):
    """Base model for resource setting models."""

    title = "Resources"
    identifier = "resources"

    global_codes = tl.Dict(
        key_trait=tl.Unicode(),
        value_trait=tl.Dict(),
    )

    warning_messages = tl.Unicode("")

    def __init__(self, *args, **kwargs):
        self.default_codes: dict[str, dict] = kwargs.pop("default_codes", {})

        super().__init__(*args, **kwargs)

        # Used by the code-setup thread to fetch code options
        self.DEFAULT_USER_EMAIL = orm.User.collection.get_default().email

    def add_model(self, identifier: str, model: CodeModel):
        super().add_model(identifier, model)
        code_key = model.default_calc_job_plugin.split(".")[-1]
        model.update(
            self.DEFAULT_USER_EMAIL,
            default_code=self.default_codes.get(code_key, {}).get("code"),
        )

    def refresh_codes(self):
        for _, code_model in self.get_models():
            code_key = code_model.default_calc_job_plugin.split(".")[-1]
            code_model.update(
                self.DEFAULT_USER_EMAIL,
                default_code=self.default_codes.get(code_key, {}).get("code"),
                refresh=True,
            )

    def get_model_state(self):
        return {
            "codes": {
                identifier: code_model.get_model_state()
                for identifier, code_model in self.get_models()
                if code_model.is_ready
            },
        }

    def set_model_state(self, parameters: dict):
        code_data = parameters.get("codes", {}) or self.default_codes
        for identifier, code_model in self.get_models():
            if identifier in code_data:
                code_model.set_model_state(code_data[identifier])

    def _check_blockers(self):
        return []
