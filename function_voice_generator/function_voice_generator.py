#!/usr/bin/env python3
"""
Function Voice Generator - Tạo audio từ text
Chạy: python function_voice_generator/function_voice_generator.py
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional, List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_REPO = "k2-fsa/OmniVoice"
SAMPLE_RATE = 24000
MODELS_DIR = PROJECT_ROOT / "Models"


def check_model():
    """Kiểm tra và tải model tự động"""
    import json

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    version_file = MODELS_DIR / "model_version.json"

    local_version = None
    if version_file.exists():
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                local_version = json.load(f).get('version')
        except Exception:
            pass

    try:
        from huggingface_hub import list_repo_files, hf_hub_download
        files = list(list_repo_files(MODEL_REPO, token=None))
        remote_version = 'unknown'
        for f in files:
            if '.json' in f:
                try:
                    downloaded = hf_hub_download(MODEL_REPO, filename=f, token=None)
                    with open(downloaded, 'r', encoding='utf-8') as fp:
                        remote_version = json.load(fp).get('version', 'unknown')
                        break
                except Exception:
                    pass
    except Exception:
        remote_version = None

    if local_version and remote_version and local_version == remote_version:
        logger.info(f"✓ Model: {local_version}")
    else:
        if not local_version:
            logger.info("Chưa có model. Đang tải...")
        else:
            logger.info(f"Cập nhật model: {local_version} -> {remote_version}")

        try:
            from omnivoice import OmniVoice
            import torch

            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            logger.info(f"Đang tải model...")
            model = OmniVoice.from_pretrained(MODEL_REPO, device_map=device, dtype=dtype)

            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump({'version': remote_version}, f)
            logger.info("✓ Tải model thành công!")
            return model
        except Exception as e:
            logger.error(f"Lỗi tải model: {e}")
            return None

    return "exists"


def load_instruct():
    """Đọc instruct từ config_voices.txt - lấy dòng không có # đầu tiên"""
    config_file = Path(__file__).parent / "config_voices.txt"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if not line.strip():
                        continue
                    return line
    logger.error("Không tìm thấy instruct trong config_voices.txt!")
    return None


def load_text():
    """Đọc text từ text.txt - mỗi dòng là một câu"""
    text_file = Path(__file__).parent / "text.txt"
    if not text_file.exists():
        logger.error(f"Không tìm thấy {text_file}")
        return []

    texts = []
    with open(text_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                texts.append(line)

    return texts


def load_model():
    """Load OmniVoice model"""
    try:
        from omnivoice import OmniVoice
        import torch
    except ImportError as e:
        logger.error(f"Thiếu thư viện: {e}")
        logger.info("Cài: pip install omnivoice torch")
        sys.exit(1)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    logger.info(f"Device: {device}, Dtype: {dtype}")

    try:
        model = OmniVoice.from_pretrained(MODEL_REPO, device_map=device, dtype=dtype)
        logger.info("✓ Model loaded!")
        return model
    except Exception as e:
        logger.error(f"Lỗi load model: {e}")
        sys.exit(1)


def generate_audio(model, text: str, instruct: str, output_file: str):
    """Tạo audio từ text với instruct"""
    try:
        import torchaudio

        kwargs = {"text": text, "instruct": instruct}

        logger.info(f"Tạo: {text[:50]}...")
        audio = model.generate(**kwargs)

        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            torchaudio.save(output_file, audio[0], SAMPLE_RATE)
            logger.info(f"✓ Lưu: {output_file}")
            return output_file
        return None
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Function Voice Generator')
    parser.add_argument('--skip-check', '-s', action='store_true', help='Bỏ qua kiểm tra model')
    args = parser.parse_args()

    logger.info("=== Function Voice Generator ===")

    instruct = load_instruct()  # Lấy instruct từ config_voices.txt
    if not instruct:
        sys.exit(1)

    logger.info(f"Instruct: {instruct}")
    texts = load_text()

    if not texts:
        logger.error("Không có text!")
        sys.exit(1)

    if not args.skip_check:
        check_result = check_model()
        if check_result == "exists":
            model = load_model()
        elif check_result is None:
            sys.exit(1)
        else:
            model = check_result
    else:
        model = load_model()

    output_dir = PROJECT_ROOT / "Output"
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, text in enumerate(texts, 1):
        filename = f"output_{i:03d}"
        output_wav = output_dir / f"{filename}_ref.wav"
        output_txt = output_dir / f"{filename}_text_ref.txt"

        result = generate_audio(model, text, instruct, str(output_wav))

        # Lưu text vào file _ref.txt
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write(text)

    logger.info(f"=== Hoàn tất! Audio trong: {output_dir} ===")


if __name__ == "__main__":
    main()