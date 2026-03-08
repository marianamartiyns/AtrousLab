from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Literal
import json

Activation = Literal["relu", "identity"]
FilterType = Literal["generic", "sobel"]

ALLOWED_ACTIVATIONS = {"relu", "identity"}
ALLOWED_FILTER_TYPES = {"generic", "sobel"}

class ConfigError(Exception):
    pass

class ConfigParseError(ConfigError):
    pass

class ConfigValidationError(ConfigError):
    pass


@dataclass(frozen=True)
class Config:
    mask: List[List[float]]
    stride: int
    r: int
    activation: Activation
    filter_type: FilterType
    mask_name: str
    config_name: str

    @property
    def m(self) -> int:
        return len(self.mask)

    @property
    def n(self) -> int:
        return len(self.mask[0]) if self.mask else 0


def load_config_from_uploads(
    *,
    config_bytes: bytes,
    config_name: str = "config.json",
    mask_bytes: bytes,
    mask_name: str = "mask.txt",
) -> Config:
    data = _read_json_bytes(config_bytes, source=config_name)

    stride = _parse_int_range(data.get("stride"), "stride", 1, 5, config_name)
    r = _parse_int_range(data.get("r"), "r", 1, 5, config_name)
    activation = _parse_activation(data.get("activation"), config_name)
    filter_type = _parse_filter_type(data.get("filter_type", "generic"), config_name)

    mask = _read_mask_bytes(mask_bytes, source=mask_name)
    mask = _validate_mask(mask, source=mask_name)

    return Config(
        mask=mask,
        stride=stride,
        r=r,
        activation=activation,
        filter_type=filter_type,
        mask_name=mask_name,
        config_name=config_name,
    )


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
        raise ConfigValidationError(
            f"Config deve ser um objeto JSON (dict). Recebido: {type(obj).__name__} ({source})"
        )

    return obj


def _read_mask_bytes(b: bytes, source: str) -> List[List[float]]:
    try:
        text = b.decode("utf-8")
    except Exception as e:
        raise ConfigParseError(f"Máscara não está em UTF-8 ({source}): {e}") from e

    lines = text.splitlines()
    rows: List[List[float]] = []

    for idx, line in enumerate(lines, start=1):
        cleaned = _strip_comment(line)
        if not cleaned:
            continue

        parts = cleaned.replace(",", " ").split()

        try:
            row = [float(value) for value in parts]
        except ValueError as e:
            raise ConfigParseError(
                f"Valor não numérico na máscara ({source}, linha {idx}): '{line}'"
            ) from e

        if len(row) == 0:
            raise ConfigValidationError(
                f"Linha inválida na máscara ({source}, linha {idx})."
            )

        rows.append(row)

    if len(rows) == 0:
        raise ConfigValidationError(f"Máscara vazia ({source}).")

    return rows


def _strip_comment(s: str) -> str:
    s = s.split("#", 1)[0]
    s = s.split("//", 1)[0]
    return s.strip()


def _validate_mask(mask: List[List[float]], source: str) -> List[List[float]]:
    if not isinstance(mask, list) or len(mask) == 0:
        raise ConfigValidationError(f"Máscara inválida ou vazia ({source}).")

    n = len(mask[0])
    if n == 0:
        raise ConfigValidationError(f"Máscara com 0 colunas ({source}).")

    for i, row in enumerate(mask):
        if len(row) != n:
            raise ConfigValidationError(
                f"Máscara deve ser retangular: linha {i} tem {len(row)} colunas, esperado {n} ({source})."
            )

    return mask


def _parse_int_range(value: Any, name: str, min_v: int, max_v: int, source: str) -> int:
    if isinstance(value, bool):
        raise ConfigValidationError(
            f"'{name}' deve ser inteiro entre {min_v} e {max_v} ({source})."
        )

    try:
        parsed = int(value)
    except Exception as e:
        raise ConfigValidationError(
            f"'{name}' deve ser inteiro entre {min_v} e {max_v} ({source})."
        ) from e

    if parsed < min_v or parsed > max_v:
        raise ConfigValidationError(
            f"'{name}' fora do intervalo {min_v}–{max_v} ({source}): {value}"
        )

    return parsed


def _parse_activation(value: Any, source: str) -> Activation:
    if value is None:
        raise ConfigValidationError(
            f"Campo obrigatório ausente: 'activation' ({source})"
        )

    act = str(value).strip().lower()
    if act not in ALLOWED_ACTIVATIONS:
        raise ConfigValidationError(
            f"'activation' inválida ({source}): '{value}'. Use 'relu' ou 'identity'."
        )

    return act  # type: ignore[return-value]


def _parse_filter_type(value: Any, source: str) -> FilterType:
    ft = str(value).strip().lower()
    if ft not in ALLOWED_FILTER_TYPES:
        raise ConfigValidationError(
            f"'filter_type' inválido ({source}): '{value}'. Use 'generic' ou 'sobel'."
        )
    return ft  # type: ignore[return-value]