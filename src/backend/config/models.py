from dataclasses import dataclass
from typing import List, Literal

Activation = Literal["relu", "identity"]

@dataclass(frozen=True)
class Config:
    mask: List[List[float]]     # matriz m×n (vinda do .txt)
    stride: int                 # 1–5
    r: int                      # 1–5
    activation: Activation      # relu / identity
    mask_file: str              # caminho original do .txt (para rastreio)

    @property
    def m(self) -> int:
        return len(self.mask)

    @property
    def n(self) -> int:
        return len(self.mask[0]) if self.mask else 0