from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from api.models import Finding


@dataclass
class DetectorContext:
    image: np.ndarray
    domain: str
    shared_features: dict[str, any] = field(default_factory=dict)


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
