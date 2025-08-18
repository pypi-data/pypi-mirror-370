#!/usr/bin/env python3
"""
Setup script for AI Prompt Engineering Game
Makes it installable via pip
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-prompt-game",
    version="1.1.0",
    author="Suraj Sahani",
    author_email="surajkumarsahani1997@gmail.com",
    description="Cross-platform AI-powered reverse prompt engineering educational game for Windows, macOS, and Linux",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/surajsahani/ai-prompt-game",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "ai-prompt-game=ai_prompt_game.cli:main",
            "prompt-game=ai_prompt_game.cli:main",
            "ai-game=ai_prompt_game.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_prompt_game": [
            "targets/*.jpg",
            "targets/*.png",
            "data/*.json",
        ],
    },
    keywords="ai, education, prompt-engineering, machine-learning, game, cli",
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "twine>=3.0",
            "build>=0.7",
        ],
        "huggingface": [
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "torchvision>=0.13.0",
            "diffusers>=0.20.0",
            "accelerate>=0.20.0",
        ],
        "replicate": [
            "replicate>=0.8.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/surajsahani/ai-prompt-game/issues",
        "Source": "https://github.com/surajsahani/ai-prompt-game",
        "Documentation": "https://github.com/surajsahani/ai-prompt-game#readme",
        "Homepage": "https://github.com/surajsahani/ai-prompt-game",
    },
)