from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class RGBImage:
    """
    Representação padrão do projeto:
      - data: np.ndarray (H, W, 3) uint8
    """
    path: str
    data: np.ndarray  # H×W×3, uint8

    @property
    def height(self) -> int:
        return int(self.data.shape[0])

    @property
    def width(self) -> int:
        return int(self.data.shape[1])