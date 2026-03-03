import json
import numpy as np
from pathlib import Path
from PIL import Image

from app.settings import OUTPUT_DIR


def apply_activation(x: np.ndarray, mode: str) -> np.ndarray:
    mode = (mode or "identity").lower()
    if mode == "relu":
        return np.maximum(0, x)
    if mode == "identity":
        return x
    raise ValueError(f"Ativação desconhecida: {mode}")


def postprocess_sobel(img: np.ndarray) -> np.ndarray:
    # img pode ser HxWx3 (float)
    img = np.abs(img)
    min_val = float(img.min())
    max_val = float(img.max())
    if max_val - min_val == 0:
        return np.zeros_like(img, dtype=np.uint8)

    img = (img - min_val) / (max_val - min_val)
    img = img * 255.0
    return img.astype(np.uint8)


def correlate2d_atrous_stride(channel: np.ndarray, kernel: np.ndarray, stride: int, r: int) -> np.ndarray:
    """
    Correlação 2D (não convolução) com:
      - stride (passo)
      - dilation rate r (atrous): espaçamento entre amostras do kernel
    Saída: H_out x W_out (float32)
    """
    if stride < 1:
        raise ValueError("stride deve ser >= 1")
    if r < 1:
        raise ValueError("r deve ser >= 1")

    h, w = channel.shape
    kh, kw = kernel.shape
    if kh % 2 == 0 or kw % 2 == 0:
        raise ValueError("mask/kernel deve ter dimensões ímpares (ex: 3x3, 5x5).")

    # tamanho efetivo do kernel com dilatação (atrous)
    eff_kh = (kh - 1) * r + 1
    eff_kw = (kw - 1) * r + 1
    pad_h = eff_kh // 2
    pad_w = eff_kw // 2

    padded = np.pad(channel, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant")

    # saída com stride: varre a imagem original em passos de 'stride'
    out_h = (h + 2 * pad_h - eff_kh) // stride + 1
    out_w = (w + 2 * pad_w - eff_kw) // stride + 1

    out = np.zeros((out_h, out_w), dtype=np.float32)

    # correlação: soma kernel[u,v] * pixel deslocado por u*r, v*r
    for oi in range(out_h):
        i = oi * stride
        for oj in range(out_w):
            j = oj * stride
            acc = 0.0
            for u in range(kh):
                for v in range(kw):
                    acc += float(kernel[u, v]) * float(padded[i + u * r, j + v * r])
            out[oi, oj] = acc

    return out


def upsample_nearest(x: np.ndarray, target_h: int, target_w: int) -> np.ndarray:
    """
    Upsample nearest neighbor (para voltar ao tamanho original quando stride>1).
    x: Hs x Ws (float)
    retorna: target_h x target_w
    """
    hs, ws = x.shape
    if hs == target_h and ws == target_w:
        return x

    # mapeamento simples
    yi = (np.linspace(0, hs - 1, target_h)).round().astype(int)
    xi = (np.linspace(0, ws - 1, target_w)).round().astype(int)
    return x[yi[:, None], xi[None, :]]


def run_pipeline(config_path: Path, image_path: Path, run_id: str) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    # -------- ler parâmetros do usuário ----------
    if "mask" not in cfg:
        raise ValueError("Config inválida: faltou 'mask' (matriz da máscara).")

    mask = np.array(cfg["mask"], dtype=np.float32)
    if mask.ndim != 2:
        raise ValueError("'mask' deve ser uma matriz 2D.")

    stride = int(cfg.get("stride", 1))
    r = int(cfg.get("r", 1))
    activation = str(cfg.get("activation", "identity"))
    filter_type = str(cfg.get("type", "generic")).lower()

    # -------- carregar imagem ----------
    image = Image.open(image_path).convert("RGB")
    img = np.array(image, dtype=np.float32)  # HxWx3
    h, w, _ = img.shape

    # -------- pipeline RGB ----------
    out_channels = []
    for c in range(3):
        ch = img[:, :, c]
        corr = correlate2d_atrous_stride(ch, mask, stride=stride, r=r)
        act = apply_activation(corr, activation)

        # volta para HxW para recombinar e salvar
        act_up = upsample_nearest(act, h, w)
        out_channels.append(act_up)

    out = np.stack(out_channels, axis=2)  # HxWx3 float

    # -------- pós-processamento específico ----------
    if filter_type == "sobel":
        out_u8 = postprocess_sobel(out)
    else:
        out_u8 = np.clip(out, 0, 255).astype(np.uint8)

    # -------- salvar ----------
    output_filename = f"{run_id}_output.png"
    output_path = OUTPUT_DIR / output_filename
    Image.fromarray(out_u8).save(output_path)

    return {
        "ok": True,
        "outputUrl": f"/outputs/{output_filename}",
        "logs": [
            f"mask={mask.shape}, stride={stride}, r={r}, activation={activation}, type={filter_type}",
            "Pipeline executado com sucesso."
        ],
    }