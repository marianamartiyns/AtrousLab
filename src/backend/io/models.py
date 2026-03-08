from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class RGBImage:
    # Representação da img (np.ndarray (H, W, 3) uint8) e caminho de origem/destino.
    path: str
    data: np.ndarray  # H x W x 3, uint8

    @property
    def height(self) -> int:
        return int(self.data.shape[0])

    @property
    def width(self) -> int:
        return int(self.data.shape[1])