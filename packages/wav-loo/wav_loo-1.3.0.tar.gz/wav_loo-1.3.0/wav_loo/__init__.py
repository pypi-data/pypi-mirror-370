"""
WAV Finder - A tool to find WAV files from URLs or local paths.
"""

__version__ = "1.3.0"
__author__ = "liuliang"
__email__ = "ioyy900205@gmail.com"

__all__ = ["WavFinder", "generate_noise_segments", "NoiseSegmentsConfig"]


def __getattr__(name):
    if name == "WavFinder":
        from .finder import WavFinder
        return WavFinder
    if name in ("generate_noise_segments", "NoiseSegmentsConfig"):
        from .noise.segments import generate_noise_segments, NoiseSegmentsConfig
        return generate_noise_segments if name == "generate_noise_segments" else NoiseSegmentsConfig
    raise AttributeError(name) 