#!/usr/bin/env python3
"""
Function CloneAudio - Kiểm tra audio mẫu voice cloning
Chạy: python function_cloneaudio/function_cloneaudio.py
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_REPO = "k2-fsa/OmniVoice"
MODELS_DIR = PROJECT_ROOT / "Models"
SAMPLE_RATE = 24000


def load_model():
    """Load OmniVoice model"""
    try:
        from omnivoice import OmniVoice
        import torch

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        logger.info(f"Loading model: device={device}, dtype={dtype}")
        model = OmniVoice.from_pretrained(MODEL_REPO, device_map=device, dtype=dtype)
        logger.info("✓ Model loaded!")
        return model
    except Exception as e:
        logger.error(f"Lỗi load model: {e}")
        return None


def generate_clone_audio(model, text, ref_audio, ref_text, output_file):
    """Tạo audio bằng voice cloning"""
    try:
        import torchaudio

        logger.info(f"Creating: {text[:50]}...")

        audio = model.generate(
            text=text,
            ref_audio=ref_audio,
            ref_text=ref_text
        )

        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        torchaudio.save(output_file, audio[0], SAMPLE_RATE)
        logger.info(f"✓ Saved: {output_file}")

        # Lưu text vào file _ref.txt
        ref_file = output_file.replace('.wav', '_ref.txt')
        with open(ref_file, 'w', encoding='utf-8') as f:
            f.write(text)

        return True
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        return False


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
        return True

    if not local_version:
        logger.info("Chưa có model. Đang tải...")
    else:
        logger.info(f"Cập nhật: {local_version} -> {remote_version}")

    try:
        from omnivoice import OmniVoice
        import torch

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        logger.info(f"Device: {device}, Dtype: {dtype}")
        model = OmniVoice.from_pretrained(MODEL_REPO, device_map=device, dtype=dtype)

        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump({'version': remote_version}, f)
        logger.info("✓ Tải model thành công!")
        return True
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        return False


def load_text():
    """Đọc text từ text.txt"""
    text_file = Path(__file__).parent / "text.txt"
    if text_file.exists():
        with open(text_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    return []


def check_audio_files():
    """Kiểm tra các file audio trong folder"""
    clone_dir = Path(__file__).parent

    audio_files = []
    for ext in ['.wav', '.mp3']:
        for f in clone_dir.glob(f'*{ext}'):
            if f.name != 'text.txt':
                audio_files.append(f)

    if not audio_files:
        logger.warning("Không có file audio!")
        return False

    logger.info(f"Tìm thấy {len(audio_files)} file audio:")
    for f in audio_files:
        size = f.stat().st_size
        size_str = f"{size/1024:.1f}KB" if size < 1024*1024 else f"{size/1024/1024:.1f}MB"
        logger.info(f"  - {f.name} ({size_str})")

    ref_audio = None
    for name in ['ref.wav', 'ref.mp3']:
        if (clone_dir / name).exists():
            ref_audio = clone_dir / name
            break

    if not ref_audio:
        ref_audio = audio_files[0]
        logger.info(f"Không có ref.wav/ref.mp3, dùng: {ref_audio.name}")

    try:
        import torchaudio
        info = torchaudio.info(str(ref_audio))
        logger.info(f"Thông tin audio:")
        logger.info(f"  - Sample rate: {info.sample_rate}")
        logger.info(f"  - Channels: {info.num_channels}")
        logger.info(f"  - Frames: {info.num_frames}")
        logger.info(f"  - Duration: {info.num_frames / info.sample_rate:.2f}s")
    except Exception as e:
        logger.warning(f"Không đọc được thông tin: {e}")

    return True


def check_text():
    """Kiểm tra text_ref.txt"""
    text_file = Path(__file__).parent / "text_ref.txt"
    if not text_file.exists():
        logger.warning("Không có text_ref.txt!")
        return False

    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    if not content:
        logger.warning("text_ref.txt trống!")
        return False

    logger.info(f"text_ref.txt: {content[:100]}...")
    return True


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Function CloneAudio')
    parser.add_argument('--check-only', '-c', action='store_true', help='Chỉ kiểm tra audio')
    parser.add_argument('--skip-model', '-s', action='store_true', help='Bỏ qua kiểm tra model')
    args = parser.parse_args()

    logger.info("=== Function CloneAudio ===")

    text = load_text()
    if text:
        logger.info(f"Text commands: {text}")

    if not args.skip_model:
        check_model()

    has_audio = check_audio_files()
    has_text = check_text()

    if args.check_only:
        logger.info("=== Kiểm tra xong ===")
        return

    if has_audio and has_text:
        logger.info("✓ Audio mẫu đã sẵn sàng!")

        # Tạo audio từ text.txt
        model = load_model()
        if not model:
            logger.error("Không load được model!")
            return

        # Đọc text từ text.txt (không phải text_ref.txt)
        text_file = Path(__file__).parent / "text.txt"
        texts = []
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        texts.append(line)

        if not texts:
            logger.warning("Không có text để tạo audio!")
            return

        # Lấy ref audio và ref text
        clone_dir = Path(__file__).parent
        ref_audio = None
        for ext in ['.wav', '.mp3']:
            for f in clone_dir.glob(f'*{ext}'):
                if f.name not in ['text.txt', 'text_ref.txt']:
                    ref_audio = str(f)
                    break
            if ref_audio:
                break

        ref_text = None
        ref_text_file = clone_dir / "text_ref.txt"
        if ref_text_file.exists():
            with open(ref_text_file, 'r', encoding='utf-8') as f:
                ref_text = f.read().strip()

        if not ref_audio:
            logger.error("Không tìm thấy ref audio!")
            return

        if not ref_text:
            logger.warning("Không có ref_text.txt, model sẽ tự transcribe!")

        logger.info(f"Using ref: {ref_audio}")
        logger.info(f"Ref text: {ref_text[:50] if ref_text else 'auto'}...")

        # Gộp tất cả text thành một đoạn
        full_text = " ".join(texts)
        logger.info(f"Full text: {full_text[:100]}...")

        from datetime import datetime

        output_dir = PROJECT_ROOT / "Output"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"clone_{timestamp}.wav"
        text_list_file = output_dir / f"clone_{timestamp}_list.txt"

        result = generate_clone_audio(model, full_text, ref_audio, ref_text, str(output_file))

        # Lưu file text gốc
        with open(text_list_file, 'w', encoding='utf-8') as f:
            for t in texts:
                f.write(t + "\n")

        logger.info(f"=== Hoàn tất! Audio trong: {output_dir} ===")

    else:
        logger.warning("⚠ Cần kiểm tra lại!")

    logger.info("=== Hoàn tất ===")


if __name__ == "__main__":
    main()