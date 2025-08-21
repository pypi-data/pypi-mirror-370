import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

# 可选进度条
try:
	from tqdm import tqdm  # type: ignore
except Exception:  # pragma: no cover
	def tqdm(iterable, **kwargs):  # type: ignore
		return iterable

from wav_loo.utils.constants import ZONE_NAMES_4, TWO_ZONE_MAPPING
from wav_loo.utils.audio import (
	scan_wavs,
	load_clean_mono,
	load_ir,
	convolve_mono_with_ir,
	ensure_dir,
	save_wav,
	pad_or_trim_channels,
)
from wav_loo.utils.ir_utils import index_ir_by_zone


@dataclass
class GenerationConfig:
	ir_root_dir: str
	clean_root_dir: str
	output_dir: str
	sample_rate: int = 16000
	num_samples: int = 60000
	zones: int = 4  # 2 或 4
	random_seed: int = 42
	max_clean_seconds: float = 30.0  # 限制最长clean时长
	presence_prob: float = 0.5  # 每个区域有人说话的概率
	# 2音区：单个区域内出现多说话人的概率与最多人数
	two_zone_multi_speaker_prob: float = 0.3
	two_zone_max_speakers_per_zone: int = 2


class CarDataGenerator:
	def __init__(self, config: GenerationConfig):
		self.config = config
		random.seed(config.random_seed)
		np.random.seed(config.random_seed)
		self.ir_by_zone: Dict[str, List[Path]] = index_ir_by_zone(Path(config.ir_root_dir), ZONE_NAMES_4)
		self.clean_wavs: List[Path] = scan_wavs(Path(config.clean_root_dir))
		os.makedirs(config.output_dir, exist_ok=True)

	def _zones_setup(self) -> Tuple[List[str], Dict[str, List[str]]]:
		if self.config.zones == 4:
			return ZONE_NAMES_4, {z: [z] for z in ZONE_NAMES_4}
		elif self.config.zones == 2:
			return ["zone_a", "zone_b"], TWO_ZONE_MAPPING
		else:
			raise ValueError("zones must be 2 or 4")

	def _choose_ir_set(self) -> Dict[str, Path]:
		chosen: Dict[str, Path] = {}
		for zone in ZONE_NAMES_4:
			candidates = self.ir_by_zone.get(zone, [])
			if not candidates:
				continue
			chosen[zone] = random.choice(candidates)
		return chosen

	def _prepare_label_contribution(self, clean_paths: List[Path], subzones: List[str], ir_choice: Dict[str, Path], num_out_ch: int, fixed_len: int) -> np.ndarray:
		"""
		计算单个逻辑区域（label）的总音频贡献。
		- 2音区/多说话人：将每个说话人随机分配到一个独立的物理位置。
		- 2音区/单说话人：随机选择一个物理位置。
		- 4音区：使用该区域所有定义的物理位置（只有一个）。
		"""
		if not clean_paths:
			return np.zeros((fixed_len, num_out_ch), dtype=np.float32)

		total_accum = np.zeros((fixed_len, num_out_ch), dtype=np.float32)
		num_speakers = len(clean_paths)
		available_subs = [s for s in subzones if ir_choice.get(s) is not None]

		if not available_subs:
			return total_accum

		if self.config.zones == 2 and num_speakers > 1:
			# 2音区、多说话人：为每个说话人分配一个独立的随机物理位置
			random.shuffle(available_subs)
			for i, clean_path in enumerate(clean_paths):
				sub = available_subs[i % len(available_subs)]  # 循环分配
				clean = load_clean_mono(clean_path, max_seconds=self.config.max_clean_seconds, sr=self.config.sample_rate)
				len_clean = clean.shape[0]
				
				ir_path = ir_choice.get(sub)
				ir = load_ir(ir_path)
				y = convolve_mono_with_ir(clean, ir)
				y = y[:len_clean, :]
				
				aa = pad_or_trim_channels(y, num_out_ch)
				total_accum[:len_clean, :] += aa.astype(np.float32)
		else:
			# 4音区 或 2音区/单说话人 场景: 只有一个说话人, 对应一个物理位置
			subzone_to_use = available_subs[0]
			if self.config.zones == 2 and num_speakers == 1:
				# 2音区单人，从多个可用位置中随机选一个
				subzone_to_use = random.choice(available_subs)

			# 只有一个说话人
			clean_path = clean_paths[0]
			clean = load_clean_mono(clean_path, max_seconds=self.config.max_clean_seconds, sr=self.config.sample_rate)
			len_clean = clean.shape[0]

			# 与唯一的物理位置进行卷积
			ir_path = ir_choice.get(subzone_to_use)
			
			ir = load_ir(ir_path)
			y = convolve_mono_with_ir(clean, ir)
			y = y[:len_clean, :]

			aa = pad_or_trim_channels(y, num_out_ch)
			total_accum[:len_clean, :] += aa.astype(np.float32)

		return total_accum

	def generate(self):
		sr = self.config.sample_rate
		out_root = Path(self.config.output_dir)
		ensure_dir(out_root)

		if not self.clean_wavs:
			raise RuntimeError("No clean wavs found under clean_root_dir")

		zone_labels, zone_mapping = self._zones_setup()
		num_out_ch = len(zone_labels)
		fixed_len = int(30.0 * sr)

		if all(len(v) == 0 for v in self.ir_by_zone.values()):
			raise RuntimeError("No IRs found under ir_root_dir by expected zone names")

		for idx in tqdm(
			range(self.config.num_samples),
			total=self.config.num_samples,
			desc="Generating",
			dynamic_ncols=True,
		):
			ir_choice = self._choose_ir_set()

			# 为每个label采样是否有人说话，并保证至少一个label为真
			presence_flags: List[bool] = [(random.random() < self.config.presence_prob) for _ in zone_labels]
			if not any(presence_flags):
				presence_flags[random.randrange(len(zone_labels))] = True

			# 为被激活的label选择clean；2音区允许同一区内多说话人
			label_idx_to_cleans: Dict[int, List[Path]] = {}
			present_indices = [i for i, p in enumerate(presence_flags) if p]
			if self.config.zones == 4:
				# 4音区：每个label固定1个说话人
				if len(self.clean_wavs) >= len(present_indices):
					chosen_paths = random.sample(self.clean_wavs, len(present_indices))
				else:
					chosen_paths = [random.choice(self.clean_wavs) for _ in present_indices]
				for i, idx_present in enumerate(present_indices):
					label_idx_to_cleans[idx_present] = [Path(chosen_paths[i])]
			else:
				# 2音区：按概率决定是否有第二位说话人，且不超过上限
				for idx_label, pflag in enumerate(presence_flags):
					if not pflag:
						continue
					n_speakers = 1 + int(random.random() < self.config.two_zone_multi_speaker_prob)
					n_speakers = min(max(1, n_speakers), self.config.two_zone_max_speakers_per_zone)
					if len(self.clean_wavs) >= n_speakers:
						paths = random.sample(self.clean_wavs, n_speakers)
					else:
						paths = [random.choice(self.clean_wavs) for _ in range(n_speakers)]
					label_idx_to_cleans[idx_label] = [Path(p) for p in paths]

			# 构建每个label的贡献（处理区内多说话人与多物理位置）
			per_label_full: List[np.ndarray] = []
			for label_idx, label in enumerate(zone_labels):
				subzones = zone_mapping[label]
				clean_paths_lbl = label_idx_to_cleans.get(label_idx, [])
				contrib = self._prepare_label_contribution(
					clean_paths_lbl,
					subzones,
					ir_choice,
					num_out_ch,
					fixed_len,
				)
				per_label_full.append(contrib)

			# 计算混合与目标
			per_label_stack = np.stack(per_label_full, axis=-1)  # (T, C, L)
			mixture_mat = np.sum(per_label_stack, axis=-1)  # (T, C)
			target_mat = np.zeros_like(mixture_mat, dtype=np.float32)
			for ch_idx in range(num_out_ch):
				target_mat[:, ch_idx] = per_label_full[ch_idx][:, ch_idx]

			uid = f"{idx:08d}"
			save_wav(out_root / f"target_{uid}.wav", target_mat, sr)
			save_wav(out_root / f"mixture_{uid}.wav", mixture_mat, sr) 