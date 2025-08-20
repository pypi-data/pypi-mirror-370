import sys
import typing as t

import ipywidgets as ipw
from aiidalab_widgets_base import LoadingWidget

from .model import PanelModel

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


PM = t.TypeVar("PM", bound=PanelModel)


class Panel(ipw.VBox, t.Generic[PM]):
    """Base class for all panels."""

    rendered = False
    _loading_message = "Loading {identifier} panel"

    # For IDE type checking
    # Type checking struggles with `traitlets.HasTraits`, which inherits
    # `traitlets.HasDescriptors`, which in turn defines `__new__(...) -> t.Any`
    def __new__(cls, *args: t.Any, **kwargs: t.Any) -> Self:
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, model: PM, **kwargs):
        loading_message = self._loading_message.format(identifier=model.identifier)
        loading_message = loading_message.replace("_", " ")
        self.loading_message: LoadingWidget = LoadingWidget(loading_message)
        super().__init__(children=[self.loading_message], **kwargs)
        self._model = model

    def render(self):
        raise NotImplementedError()
