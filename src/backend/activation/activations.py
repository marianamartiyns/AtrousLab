from __future__ import annotations
from typing import Literal
import numpy as np

ActivationType = Literal["relu", "identity"]

class ActivationError(Exception):
    pass

def apply_activation(x: np.ndarray, activation: ActivationType) -> np.ndarray:
    """
    Aplica a ativação APÓS o somatório (isto é, após a correlação/convolução).

    - x pode ser:
        - 2D (H×W) para um canal
        - 3D (H×W×3) para RGB
    - Retorna uma cópia (float32) com a ativação aplicada.
    """
    if not isinstance(x, np.ndarray):
        raise ActivationError("x deve ser np.ndarray")
    if x.ndim not in (2, 3):
        raise ActivationError(f"x deve ser 2D ou 3D. Obtido: {x.ndim}D")
    if x.ndim == 3 and x.shape[2] != 3:
        raise ActivationError(f"x 3D deve ser H×W×3. Obtido: {x.shape}")

    act = str(activation).strip().lower()
    if act not in ("relu", "identity"):
        raise ActivationError(f"Ativação inválida: '{activation}'. Use 'relu' ou 'identity'.")

    xf = x.astype(np.float32, copy=False)

    if act == "identity":
        return xf.copy()

    # ReLU: max(0, x)
    return np.maximum(xf, 0.0)


def relu(x: np.ndarray) -> np.ndarray:
    """Atalho para ReLU."""
    if not isinstance(x, np.ndarray):
        raise ActivationError("x deve ser np.ndarray")
    return np.maximum(x.astype(np.float32, copy=False), 0.0)


def identity(x: np.ndarray) -> np.ndarray:
    """Atalho para identidade."""
    if not isinstance(x, np.ndarray):
        raise ActivationError("x deve ser np.ndarray")
    return x.astype(np.float32, copy=False).copy()