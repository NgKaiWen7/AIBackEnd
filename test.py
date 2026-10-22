#!/usr/bin/env python3
"""Generate card art for linux_cards_deck.json with Z-Image-Turbo (local, CPU-friendly).

Quantization modes (--quant):
  none  full bf16 weights (~20 GB RAM for transformer + text encoder)
  int8  weight-only INT8 via optimum-quanto   (pip install optimum-quanto)
  gguf  GGUF transformer, e.g. Q4_K_M         (pip install gguf; pass --gguf FILE)
Add --quant-text to also INT8-quantize the ~4B Qwen3 text encoder (works with int8 or gguf).

Examples:
  python generate_art_quant.py --quant int8 --quant-text --width 768 --height 768 --seeds 2
  python generate_art_quant.py --quant gguf --gguf ./models/z-image-turbo-Q4_K_M.gguf --quant-text
  python generate_art_quant.py --only chmod kill --seeds 8
"""

import argparse
import json
import time
from pathlib import Path

import torch
from diffusers import ZImagePipeline, ZImageTransformer2DModel
from PIL import Image

DTYPES = {"bf16": torch.bfloat16, "fp32": torch.float32}


def build_contact_sheet(paths, out_path, thumb=256):
    """Tile the candidates in one row so you can pick the best seed quickly."""
    paths = [p for p in paths if Path(p).exists()]
    if not paths:
        return
    sheet = Image.new("RGB", (thumb * len(paths), thumb), "white")
    for i, p in enumerate(paths):
        img = Image.open(p).convert("RGB").resize((thumb, thumb))
        sheet.paste(img, (i * thumb, 0))
    sheet.save(out_path)


def quantize_int8(module):
    from optimum.quanto import freeze, qint8, quantize

    quantize(module, weights=qint8)
    freeze(module)


def load_pipeline(args):
    dtype = DTYPES[args.dtype]
    common = dict(torch_dtype=dtype, local_files_only=True)

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Check your PyTorch installation.")

    if args.quant == "gguf":
        if not args.gguf:
            raise SystemExit("--quant gguf needs --gguf /path/to/file.gguf")

        from diffusers import GGUFQuantizationConfig

        transformer = ZImageTransformer2DModel.from_single_file(
            args.gguf,
            quantization_config=GGUFQuantizationConfig(compute_dtype=dtype),
            config=args.model,
            subfolder="transformer",
            **common,
        )

        pipe = ZImagePipeline.from_pretrained(
            args.model, transformer=transformer, **common
        )

    elif args.quant == "int8":
        transformer = ZImageTransformer2DModel.from_pretrained(
            args.model, subfolder="transformer", **common
        )
        quantize_int8(transformer)

        pipe = ZImagePipeline.from_pretrained(
            args.model, transformer=transformer, **common
        )

    else:
        pipe = ZImagePipeline.from_pretrained(args.model, **common)

    if args.quant_text:
        quantize_int8(pipe.text_encoder)

    try:
        pipe.vae.enable_tiling()

    except Exception:
        pass

    # Move the pipeline to GPU.
    pipe.enable_model_cpu_offload()

    print(f"Pipeline device: {pipe.device}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GiB")

    return pipe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", default="linux_cards_deck.json")
    ap.add_argument("--out", default="art")
    ap.add_argument(
        "--model", default="./models/Z-Image-Turbo", help="Local model directory"
    )
    ap.add_argument("--quant", choices=["none", "int8", "gguf"], default="gguf")
    ap.add_argument(
        "--gguf",
        default="./models/z-image-turbo-Q4_K_M.gguf",
        help="Path to a local Z-Image-Turbo .gguf (for --quant gguf)",
    )
    ap.add_argument(
        "--quant-text", action="store_true", help="INT8-quantize the text encoder too"
    )
    ap.add_argument(
        "--dtype",
        choices=list(DTYPES),
        default="bf16",
        help="compute dtype; try fp32 only if your CPU lacks fast bf16 AND you have the RAM",
    )
    ap.add_argument(
        "--threads", type=int, default=0, help="torch CPU threads (0 = PyTorch default)"
    )
    ap.add_argument("--seeds", type=int, default=4, help="candidates per card")
    ap.add_argument("--seed-start", type=int, default=0)
    ap.add_argument("--width", type=int, default=1024)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=8)
    ap.add_argument("--only", nargs="*", help="card ids to generate")
    args = ap.parse_args()

    if args.threads > 0:
        torch.set_num_threads(args.threads)

    pipe = load_pipeline(args)
    path = "image.png"
    image = pipe(
        "side view, a hot sexy girl, naked with hot short pants and tied up around boobs",
        height=args.height,
        width=args.width,
        num_inference_steps=args.steps,
        guidance_scale=0.0,  # Turbo is distilled: CFG must stay at 0
        generator=torch.Generator("cuda").manual_seed(10),
    ).images[0]
    image.save(path)


if __name__ == "__main__":
    main()
