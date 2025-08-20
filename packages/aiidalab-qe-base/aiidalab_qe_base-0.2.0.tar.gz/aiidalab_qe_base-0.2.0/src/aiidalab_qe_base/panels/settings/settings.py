from __future__ import annotations

import typing as t
import traitlets as tl

from ..panel import Panel
from .model import SettingsModel

SM = t.TypeVar("SM", bound=SettingsModel)


class SettingsPanel(Panel[SM]):
    """Base model for settings panels."""

    updated = False

    def __init__(self, model: SM, **kwargs):
        super().__init__(model=model, **kwargs)
        self.links: list[tl.dlink | tl.link] = []
