from __future__ import annotations

import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import numpy as np
import soundfile as sf


@dataclass
class NoiseSegmentsConfig:
	input_dir: Path
	output_dir: Path
	duration_seconds: float = 30.0
	total_segments: int = 60000
	random_seed: int = 42


def _find_wavs(input_dir: Path) -> List[Path]:
	return sorted([p for p in input_dir.rglob('*.wav') if p.is_file()])


def _read_wav_int16(path: Path) -> Tuple[np.ndarray, int, int]:
	"""
	Read WAV as int16 frames, preserving channels.
	Returns (audio_int16 [num_frames, channels], sample_rate, num_channels)
	"""
	audio, sr = sf.read(str(path), dtype='int16', always_2d=True)
	# shape: (frames, channels)
	num_channels = audio.shape[1]
	return audio, sr, num_channels


def _write_wav_int16(path: Path, audio_int16: np.ndarray, sr: int, num_channels: int) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	sf.write(str(path), audio_int16, sr, subtype='PCM_16')


def _extract_random_segment(audio_int16: np.ndarray, segment_samples: int) -> np.ndarray:
	num_samples = audio_int16.shape[0]
	if num_samples >= segment_samples:
		start = random.randint(0, num_samples - segment_samples)
		return audio_int16[start:start + segment_samples]
	else:
		channels = audio_int16.shape[1] if audio_int16.ndim > 1 else 1
		seg = np.zeros((segment_samples, channels), dtype=np.int16)
		seg[:num_samples] = audio_int16
		return seg


def generate_noise_segments(cfg: NoiseSegmentsConfig) -> int:
	"""
	Generate noise segments from input directory of WAV files.
	Returns the number of segments generated.
	"""
	random.seed(cfg.random_seed)
	input_dir = cfg.input_dir
	output_dir = cfg.output_dir
	output_dir.mkdir(parents=True, exist_ok=True)

	wavs = _find_wavs(input_dir)
	if len(wavs) == 0:
		print(f"No WAV files found in {input_dir}")
		return 0

	target_total = cfg.total_segments if cfg.total_segments and cfg.total_segments > 0 else len(wavs)

	start_t = time.time()
	generated = 0
	num_files = len(wavs)
	for idx, wav_path in enumerate(wavs, 1):
		if generated >= target_total:
			break
		try:
			audio, sr, ch = _read_wav_int16(wav_path)
		except Exception as e:
			print(f"Skip (read failed): {wav_path.name} -> {e}")
			continue

		segment_samples = int(cfg.duration_seconds * sr)
		remaining_files = num_files - idx + 1
		remaining = target_total - generated
		per_file_this = (remaining + remaining_files - 1) // remaining_files
		for k in range(per_file_this):
			if generated >= target_total:
				break
			segment = _extract_random_segment(audio, segment_samples)
			stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
			stem = wav_path.stem
			out_name = f"{stem}_seg{idx:05d}_{k:02d}_{stamp}.wav"
			out_path = output_dir / out_name
			_write_wav_int16(out_path, segment, sr, ch)
			generated += 1

	elapsed = time.time() - start_t
	print(f"Generated {generated} segments in {elapsed:.2f}s")
	return generated 