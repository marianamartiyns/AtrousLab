from __future__ import annotations

import numpy as np
from typing import Literal

ActivationName = Literal["relu", "identity"]


class ActivationError(Exception):
    pass


def relu(x: np.ndarray) -> np.ndarray:
    """
    ReLU: f(x) = max(0, x)
    """
    if not isinstance(x, np.ndarray):
        raise ActivationError("relu espera np.ndarray.")
    return np.maximum(x, 0).astype(np.float32, copy=False)


def identity(x: np.ndarray) -> np.ndarray:
    """
    Identidade: f(x) = x
    """
    if not isinstance(x, np.ndarray):
        raise ActivationError("identity espera np.ndarray.")
    return x.astype(np.float32, copy=False)


def apply_activation(x: np.ndarray, activation: ActivationName) -> np.ndarray:
    """
    Aplica a função de ativação ao resultado da correlação.
    """
    if not isinstance(x, np.ndarray):
        raise ActivationError("apply_activation espera np.ndarray.")

    act = str(activation).strip().lower()

    if act == "relu":
        return relu(x)
    if act == "identity":
        return identity(x)

    raise ActivationError(
        f"Ativação inválida: '{activation}'. Use 'relu' ou 'identity'."
    )