from pathlib import Path
from typing import List, Optional

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve


def scan_wavs(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.wav") if p.is_file()]


def load_clean_mono(path: Path, max_seconds: Optional[float] = None, sr: int = 16000) -> np.ndarray:
    audio, _sr = sf.read(str(path), always_2d=True)
    if audio.shape[1] > 1:
        audio = np.mean(audio, axis=1)
    else:
        audio = audio[:, 0]
    audio = audio.astype(np.float32)
    
    # 如果指定了最大时长限制，则截断音频
    if max_seconds is not None:
        audio = truncate_audio(audio, max_seconds, sr)
    
    return audio


def load_ir(path: Path) -> np.ndarray:
    ir, _sr = sf.read(str(path), always_2d=True)
    return ir.astype(np.float32)


def truncate_audio(audio: np.ndarray, max_seconds: float, sr: int) -> np.ndarray:
    max_len = int(max_seconds * sr)
    if audio.ndim == 1:
        return audio[:max_len]
    return audio[:max_len, ...]


def convolve_mono_with_ir(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    x2 = x[:, None]
    h2 = h[:, None] if h.ndim == 1 else h
    y = fftconvolve(x2, h2, mode="full", axes=0)
    return y.astype(np.float32)


def normalize_audio(audio: np.ndarray, peak: float = 0.99) -> np.ndarray:
    max_val = float(np.max(np.abs(audio))) if audio.size else 0.0
    if max_val > 0:
        return (audio / max_val) * peak
    return audio


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def save_wav(path: Path, audio: np.ndarray, sr: int):
    sf.write(str(path), audio.astype(np.float32), sr)


def pad_or_trim_channels(a: np.ndarray, num_out_ch: int) -> np.ndarray:
    if a.ndim == 1:
        a = a[:, None]
    if a.shape[1] < num_out_ch:
        a = np.pad(a, ((0, 0), (0, num_out_ch - a.shape[1])))
    elif a.shape[1] > num_out_ch:
        a = a[:, :num_out_ch]
    return a 