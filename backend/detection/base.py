from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from api.models import Finding


@dataclass(frozen=True)
class DetectorContext:
    image: np.ndarray
    domain: str


class BaseDetector(ABC):
    name: str = "base"

    @abstractmethod
    def detect(self, context: DetectorContext) -> list[Finding]:
        """Return candidate findings for the provided page context."""


class NoOpDetector(BaseDetector):
    name = "noop"

    def detect(self, context: DetectorContext) -> list[Finding]:
        _ = context
        return []
