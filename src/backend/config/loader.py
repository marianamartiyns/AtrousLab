from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .errors import (
    ConfigFileNotFound,
    ConfigParseError,
    ConfigValidationError,
)
from .models import Config

ALLOWED_ACTIVATIONS = {"relu", "identity"}


def load_config(config_json_path: str | Path) -> Config:
    """
    Padrão do projeto:
      - Config -> .json (stride, r, activation, mask_file)
      - Máscara -> .txt (apenas matriz m×n)
    """
    config_path = Path(config_json_path)

    if not config_path.exists():
        raise ConfigFileNotFound(f"Config .json não encontrada: {config_path}")

    if config_path.suffix.lower() != ".json":
        raise ConfigParseError(
            f"Config deve ser .json. Recebido: {config_path.name}"
        )

    data = _read_json(config_path)

    # mask_file pode ser relativo ao config.json
    mask_file_raw = data.get("mask_file")
    if not mask_file_raw:
        raise ConfigValidationError(
            f"Campo obrigatório ausente: 'mask_file' (config: {config_path})"
        )

    mask_path = Path(mask_file_raw)
    if not mask_path.is_absolute():
        mask_path = (config_path.parent / mask_path).resolve()

    mask = _read_mask_txt(mask_path)

    stride = _parse_int_range(data.get("stride"), "stride", 1, 5, str(config_path))
    r = _parse_int_range(data.get("r"), "r", 1, 5, str(config_path))
    activation = _parse_activation(data.get("activation"), str(config_path))

    # valida máscara depois de ler
    mask = _validate_mask(mask, source=str(mask_path))

    return Config(
        mask=mask,
        stride=stride,
        r=r,
        activation=activation,
        mask_file=str(mask_path),
    )


def _read_json(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigParseError(
            f"JSON inválido em {p}: linha {e.lineno}, coluna {e.colno}: {e.msg}"
        ) from e
    except Exception as e:
        raise ConfigParseError(f"Falha ao ler JSON em {p}: {e}") from e


def _read_mask_txt(p: Path) -> List[List[float]]:
    """
    TXT da máscara: apenas matriz m×n.
    - Ignora linhas vazias
    - Permite comentários com # ou //
    - Separadores: espaço e/ou vírgula
    """
    if not p.exists():
        raise ConfigFileNotFound(f"Arquivo de máscara (.txt) não encontrado: {p}")

    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        raise ConfigParseError(f"Falha ao ler máscara TXT em {p}: {e}") from e

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
                f"Valor não numérico na máscara em {p} (linha {idx}): '{line}'"
            ) from e

        if len(row) == 0:
            raise ConfigParseError(f"Linha vazia na máscara em {p} (linha {idx}).")

        rows.append(row)

    if not rows:
        raise ConfigValidationError(f"Máscara vazia em {p}.")

    return rows


def _validate_mask(mask: List[List[float]], source: str) -> List[List[float]]:
    # retangular
    n = len(mask[0])
    if n == 0:
        raise ConfigValidationError(f"'mask' inválida (0 colunas) em {source}.")

    for i, row in enumerate(mask):
        if len(row) != n:
            raise ConfigValidationError(
                f"'mask' deve ser retangular: linha {i} tem {len(row)} colunas, esperado {n} (arquivo: {source})."
            )

    # aqui você pode colocar regras extras se quiser (ex: limitar m,n)
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


def _parse_activation(value: Any, source: str) -> str:
    if value is None:
        raise ConfigValidationError(f"Campo obrigatório ausente: 'activation' (config: {source})")

    act = str(value).strip().lower()
    if act not in ALLOWED_ACTIVATIONS:
        raise ConfigValidationError(
            f"'activation' inválida (config: {source}): '{value}'. Use: relu ou identity."
        )
    return act