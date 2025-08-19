"""
WAV Finder - A tool to find WAV files from URLs or local paths.
"""

__version__ = "1.2.1"
__author__ = "liuliang"
__email__ = "ioyy900205@gmail.com"

__all__ = ["WavFinder"]


def __getattr__(name):
    if name == "WavFinder":
        from .finder import WavFinder
        return WavFinder
    raise AttributeError(name) 