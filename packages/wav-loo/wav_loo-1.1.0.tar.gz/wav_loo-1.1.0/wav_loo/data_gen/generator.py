import os
import random
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import soundfile as sf
import numpy as np
from scipy.signal import convolve  # require scipy


ZONE_NAMES_4 = [
    "zhujia",
    "fujia",
    "zhujiahoupai",
    "fujiahoupai",
]

TWO_ZONE_MAPPING = {
    "zone_a": ["zhujia", "zhujiahoupai"],
    "zone_b": ["fujia", "fujiahoupai"],
}


@dataclass
class GenerationConfig:
    ir_root_dir: str
    clean_root_dir: str
    output_dir: str
    sample_rate: int = 16000
    num_samples: int = 60000
    zones: int = 4  # 2 or 4
    random_seed: int = 42
    normalize: bool = False
    max_clean_seconds: float = 30.0  # truncate long cleans
    presence_prob: float = 0.5  # probability a zone contains the person


class CarDataGenerator:
    def __init__(self, config: GenerationConfig):
        self.config = config
        random.seed(config.random_seed)
        np.random.seed(config.random_seed)
        self.ir_by_zone: Dict[str, List[Path]] = self._index_ir_by_zone(Path(config.ir_root_dir))
        self.clean_wavs: List[Path] = self._scan_wavs(Path(config.clean_root_dir))
        os.makedirs(config.output_dir, exist_ok=True)

    def _scan_wavs(self, root: Path) -> List[Path]:
        return [p for p in root.rglob("*.wav") if p.is_file()]

    def _match_zone_from_name(self, name_lower: str) -> Optional[str]:
        # Use boundary-aware regex to avoid substring collisions; prefer longest match
        matches: List[str] = []
        for zone in ZONE_NAMES_4:
            pattern = rf"(^|[^a-z]){re.escape(zone)}([^a-z]|$)"
            if re.search(pattern, name_lower):
                matches.append(zone)
        if not matches:
            return None
        # choose the longest zone name if multiple match
        matches.sort(key=len, reverse=True)
        return matches[0]

    def _index_ir_by_zone(self, root: Path) -> Dict[str, List[Path]]:
        zone_to_files: Dict[str, List[Path]] = {z: [] for z in ZONE_NAMES_4}
        if not root.exists():
            return zone_to_files
        for sub in root.rglob("*"):
            if not sub.is_dir():
                continue
            name_lower = sub.name.lower()
            matched_zone = self._match_zone_from_name(name_lower)
            if matched_zone is None:
                continue
            files = [p for p in sub.rglob("*.wav") if p.is_file()]
            if files:
                zone_to_files[matched_zone].extend(files)
        # de-duplicate and sort for determinism
        for z in zone_to_files:
            unique = sorted({p.resolve() for p in zone_to_files[z]})
            zone_to_files[z] = [Path(p) for p in unique]
        return zone_to_files

    def _choose_ir_set(self) -> Dict[str, Path]:
        chosen: Dict[str, Path] = {}
        for zone in ZONE_NAMES_4:
            candidates = self.ir_by_zone.get(zone, [])
            if not candidates:
                continue
            chosen[zone] = random.choice(candidates)
        return chosen

    def _load_clean(self, path: Path, target_sr: int) -> np.ndarray:
        audio, sr = sf.read(str(path), always_2d=True)
        # mix to mono if multi-channel clean
        if audio.shape[1] > 1:
            audio = np.mean(audio, axis=1, keepdims=False)
        else:
            audio = audio[:, 0]
        if sr != target_sr:
            audio = self._resample_1d(audio, sr, target_sr)
        return audio.astype(np.float32)

    def _load_ir(self, path: Path, target_sr: int) -> np.ndarray:
        # return shape (n_samples, n_channels)
        ir, sr = sf.read(str(path), always_2d=True)
        if sr != target_sr:
            # resample each channel
            channels = []
            for c in range(ir.shape[1]):
                channels.append(self._resample_1d(ir[:, c], sr, target_sr))
            # pad to same length
            max_len = max(ch.shape[0] for ch in channels)
            channels = [np.pad(ch, (0, max_len - ch.shape[0])) for ch in channels]
            ir = np.stack(channels, axis=1)
        return ir.astype(np.float32)

    def _resample_1d(self, x: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
        if src_sr == dst_sr:
            return x.astype(np.float32)
        duration = x.shape[0] / src_sr
        new_len = int(round(duration * dst_sr))
        if new_len <= 1:
            return x.astype(np.float32)
        x_old = np.linspace(0.0, 1.0, num=x.shape[0], endpoint=False)
        x_new = np.linspace(0.0, 1.0, num=new_len, endpoint=False)
        return np.interp(x_new, x_old, x).astype(np.float32)

    def _truncate(self, audio: np.ndarray, max_seconds: float, sr: int) -> np.ndarray:
        max_len = int(max_seconds * sr)
        if audio.ndim == 1:
            if audio.shape[0] > max_len:
                return audio[:max_len]
            return audio
        else:
            if audio.shape[0] > max_len:
                return audio[:max_len, ...]
            return audio

    def _convolve_mono_with_ir(self, x: np.ndarray, h: np.ndarray) -> np.ndarray:
        # x: (T,), h: (L,) or (L, C) -> y: (T+L-1, C)
        if h.ndim == 1:
            y = convolve(x, h, mode="full", method="direct")
            return y[:, None].astype(np.float32)
        outputs: List[np.ndarray] = []
        for c in range(h.shape[1]):
            yc = convolve(x, h[:, c], mode="full", method="direct")
            outputs.append(yc.astype(np.float32))
        max_len = max(y.shape[0] for y in outputs)
        outputs = [np.pad(y, (0, max_len - y.shape[0])) for y in outputs]
        return np.stack(outputs, axis=1)

    def _normalize(self, audio: np.ndarray, peak: float = 0.99) -> np.ndarray:
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return (audio / max_val) * peak
        return audio

    def _mix_targets(self, targets: List[np.ndarray]) -> np.ndarray:
        # Support list of (T, C) arrays (or (T,) which will be treated as (T,1))
        max_len = 0
        max_ch = 1
        prepared: List[np.ndarray] = []
        for t in targets:
            if t.ndim == 1:
                t = t[:, None]
            max_len = max(max_len, t.shape[0])
            max_ch = max(max_ch, t.shape[1])
            prepared.append(t)
        padded: List[np.ndarray] = []
        for t in prepared:
            t_pad = t
            if t_pad.shape[0] < max_len:
                t_pad = np.pad(t_pad, ((0, max_len - t_pad.shape[0]), (0, 0)))
            if t_pad.shape[1] < max_ch:
                t_pad = np.pad(t_pad, ((0, 0), (0, max_ch - t_pad.shape[1])))
            padded.append(t_pad)
        mix = np.sum(np.stack(padded, axis=0), axis=0)
        return mix

    def _ensure_dir(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def _save_wav(self, path: Path, audio: np.ndarray, sr: int):
        # audio shape: (T,) or (T,C)
        sf.write(str(path), audio.astype(np.float32), sr)

    def _zones_setup(self) -> Tuple[List[str], Dict[str, List[str]]]:
        if self.config.zones == 4:
            return ZONE_NAMES_4, {z: [z] for z in ZONE_NAMES_4}
        elif self.config.zones == 2:
            return ["zone_a", "zone_b"], TWO_ZONE_MAPPING
        else:
            raise ValueError("zones must be 2 or 4")

    def generate(self):
        sr = self.config.sample_rate
        out_root = Path(self.config.output_dir)
        self._ensure_dir(out_root)

        if not self.clean_wavs:
            raise RuntimeError("No clean wavs found under clean_root_dir")

        zone_labels, zone_mapping = self._zones_setup()
        num_out_ch = len(zone_labels)

        # sanity: ensure IRs exist for at least one zone
        if all(len(v) == 0 for v in self.ir_by_zone.values()):
            raise RuntimeError("No IRs found under ir_root_dir by expected zone names")

        for idx in range(self.config.num_samples):
            clean_path = random.choice(self.clean_wavs)
            clean = self._load_clean(clean_path, sr)
            clean = self._truncate(clean, self.config.max_clean_seconds, sr)

            ir_choice = self._choose_ir_set()

            # compute per-label multi-channel contribution (T, C)
            per_label_full: List[np.ndarray] = []
            presence_flags: List[bool] = []
            for label in zone_labels:
                subzones = zone_mapping[label]
                present = random.random() < self.config.presence_prob
                presence_flags.append(present)
                if not present:
                    per_label_full.append(np.zeros((clean.shape[0], num_out_ch), dtype=np.float32))
                    continue

                accum_list: List[np.ndarray] = []
                for sub in subzones:
                    ir_path = ir_choice.get(sub)
                    if ir_path is None:
                        continue
                    ir = self._load_ir(ir_path, sr)  # (T_ir, C)
                    y = self._convolve_mono_with_ir(clean, ir)  # (T_out, C)
                    accum_list.append(y.astype(np.float32))
                if not accum_list:
                    per_label_full.append(np.zeros((clean.shape[0], num_out_ch), dtype=np.float32))
                else:
                    # sum subzone contributions with padding and channel alignment
                    max_len = max(a.shape[0] for a in accum_list)
                    max_ch = max(a.shape[1] for a in accum_list)
                    padded = []
                    for a in accum_list:
                        aa = a
                        if aa.shape[0] < max_len:
                            aa = np.pad(aa, ((0, max_len - aa.shape[0]), (0, 0)))
                        if aa.shape[1] < max_ch:
                            aa = np.pad(aa, ((0, 0), (0, max_ch - aa.shape[1])))
                        padded.append(aa)
                    y_sum = np.sum(np.stack(padded, axis=0), axis=0)  # (max_len, max_ch)
                    # ensure channel count equals expected output channels by pad/truncate
                    if y_sum.shape[1] < num_out_ch:
                        y_sum = np.pad(y_sum, ((0, 0), (0, num_out_ch - y_sum.shape[1])))
                    elif y_sum.shape[1] > num_out_ch:
                        y_sum = y_sum[:, :num_out_ch]
                    per_label_full.append(y_sum.astype(np.float32))

            # pad all per-label to common length
            max_len_all = max(m.shape[0] for m in per_label_full)
            per_label_full = [m if m.shape[0] == max_len_all else np.pad(m, ((0, max_len_all - m.shape[0]), (0, 0))) for m in per_label_full]

            # mixture: sum across labels along a new last dimension -> (T, num_out_ch)
            mixture_mat = np.sum(np.stack(per_label_full, axis=-1), axis=-1)

            # target: (T, num_out_ch), channel i takes label i's contribution at the same channel index
            target_mat = np.zeros_like(mixture_mat, dtype=np.float32)
            for ch_idx, m in enumerate(per_label_full):
                # place only the corresponding channel of that label
                target_mat[:, ch_idx] = m[:, ch_idx]

            if self.config.normalize:
                # peak normalize per-file
                peak = np.max(np.abs(target_mat))
                if peak > 0:
                    target_mat = target_mat / peak * 0.99
                peak_m = np.max(np.abs(mixture_mat))
                if peak_m > 0:
                    mixture_mat = mixture_mat / peak_m * 0.99

            uid = f"{idx:08d}"
            self._save_wav(out_root / f"target_{uid}.wav", target_mat, sr)
            self._save_wav(out_root / f"mixture_{uid}.wav", mixture_mat, sr) 