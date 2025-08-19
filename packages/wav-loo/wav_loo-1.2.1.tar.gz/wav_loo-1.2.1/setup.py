from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wav-loo",
    version="1.2.1",
    author="liuliang",
    author_email="ioyy900205@gmail.com",
    description="A multi-tool: WAV finder, multi-zone data generator (2/4 zones, multi-channel IR), and CLI aliases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ioyy900205/loolang_tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "urllib3>=1.26.0",
        "soundfile>=0.12.1",
        "scipy>=1.10.0",
    ],
    entry_points={
        "console_scripts": [
            "wav-loo=wav_loo.cli:main",
        ],
    },
) 