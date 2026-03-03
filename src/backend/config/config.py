# app/config.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
import json
from pathlib import Path

Activation = Literal["relu", "identity"]
ALLOWED_ACTIVATIONS = {"relu", "identity"}


# --- Errors ---
class ConfigError(Exception):
    pass

class ConfigFileNotFound(ConfigError):
    pass

class ConfigParseError(ConfigError):
    pass

class ConfigValidationError(ConfigError):
    pass


# --- Model ---
@dataclass(frozen=True)
class Config:
    mask: List[List[float]]     # matriz m×n (vinda do arquivo de máscara do usuário)
    stride: int                 # 1–5
    r: int                      # 1–5
    activation: Activation      # relu / identity
    mask_name: str              # nome original do arquivo enviado (rastreamento)
    config_name: str            # nome original do config enviado (rastreamento)

    @property
    def m(self) -> int:
        return len(self.mask)

    @property
    def n(self) -> int:
        return len(self.mask[0]) if self.mask else 0


# --- Public API: carregar config + máscara vindos do usuário ---
def load_config_from_uploads(
    *,
    config_bytes: bytes,
    config_name: str = "config.json",
    mask_bytes: bytes,
    mask_name: str = "mask.txt",
) -> Config:
    """
    Novo padrão:
      - config.json (UPLOAD do usuário): stride, r, activation
      - máscara (UPLOAD do usuário): matriz m×n
    """
    data = _read_json_bytes(config_bytes, source=config_name)
    stride = _parse_int_range(data.get("stride"), "stride", 1, 5, config_name)
    r = _parse_int_range(data.get("r"), "r", 1, 5, config_name)
    activation = _parse_activation(data.get("activation"), config_name)

    mask = _read_mask_bytes(mask_bytes, source=mask_name)
    mask = _validate_mask(mask, source=mask_name)

    return Config(
        mask=mask,
        stride=stride,
        r=r,
        activation=activation,  # type: ignore[assignment]
        mask_name=mask_name,
        config_name=config_name,
    )


# --- Helpers ---
def _read_json_bytes(b: bytes, source: str) -> Dict[str, Any]:
    try:
        text = b.decode("utf-8")
    except Exception as e:
        raise ConfigParseError(f"Config JSON não está em UTF-8 ({source}): {e}") from e

    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        raise ConfigParseError(
            f"JSON inválido em {source}: linha {e.lineno}, coluna {e.colno}: {e.msg}"
        ) from e

    if not isinstance(obj, dict):
        raise ConfigValidationError(f"Config deve ser um objeto JSON (dict). Recebido: {type(obj).__name__} ({source})")

    return obj


def _read_mask_bytes(b: bytes, source: str) -> List[List[float]]:
    """
    Máscara em TXT:
      - ignora linhas vazias
      - permite comentários # ou //
      - separadores: espaço e/ou vírgula
    """
    try:
        text = b.decode("utf-8")
    except Exception as e:
        raise ConfigParseError(f"Máscara não está em UTF-8 ({source}): {e}") from e

    lines = text.splitlines()

    def strip_comment(s: str) -> str:
        s = s.split("#", 1)[0]
        s = s.split("//", 1)[0]
        return s.strip()

    rows: List[List[float]] = []
    for idx, line in enumerate(lines, start=1):
        raw = strip_comment(line)
        if not raw:
            continue

        parts = raw.replace(",", " ").split()
        try:
            row = [float(x) for x in parts]
        except ValueError as e:
            raise ConfigParseError(
                f"Valor não numérico na máscara ({source}, linha {idx}): '{line}'"
            ) from e

        if not row:
            raise ConfigParseError(f"Linha vazia na máscara ({source}, linha {idx}).")

        rows.append(row)

    if not rows:
        raise ConfigValidationError(f"Máscara vazia ({source}).")

    return rows


def _validate_mask(mask: List[List[float]], source: str) -> List[List[float]]:
    n = len(mask[0])
    if n == 0:
        raise ConfigValidationError(f"'mask' inválida (0 colunas) em {source}.")

    for i, row in enumerate(mask):
        if len(row) != n:
            raise ConfigValidationError(
                f"'mask' deve ser retangular: linha {i} tem {len(row)} colunas, esperado {n} (arquivo: {source})."
            )

    return mask


def _parse_int_range(value: Any, name: str, min_v: int, max_v: int, source: str) -> int:
    try:
        v = int(value) if not isinstance(value, bool) else None
    except Exception as e:
        raise ConfigValidationError(
            f"'{name}' deve ser inteiro entre {min_v} e {max_v} (config: {source})."
        ) from e

    if v is None or v < min_v or v > max_v:
        raise ConfigValidationError(
            f"'{name}' fora do intervalo {min_v}–{max_v} (config: {source}): {value}"
        )
    return v


def _parse_activation(value: Any, source: str) -> Activation:
    if value is None:
        raise ConfigValidationError(f"Campo obrigatório ausente: 'activation' (config: {source})")

    act = str(value).strip().lower()
    if act not in ALLOWED_ACTIVATIONS:
        raise ConfigValidationError(
            f"'activation' inválida (config: {source}): '{value}'. Use: relu ou identity."
        )
    return act  # type: ignore[return-value]