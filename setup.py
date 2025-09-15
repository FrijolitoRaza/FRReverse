#!/usr/bin/env python3
"""
Setup script para Face Recognition Video Analyzer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README para descripción larga
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Leer requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()
requirements = [req for req in requirements if not req.startswith('#') and req.strip()]

setup(
    name="face-recognition-analyzer",
    version="2.0.0",
    author="Tu Nombre",
    author_email="tu.email@ejemplo.com",
    description="Sistema avanzado de análisis de rostros en videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tu-usuario/face-recognition-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.6.1",
        ],
        "gpu": [
            "dlib-gpu>=19.24.2",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "face-analyzer=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="face-recognition video-analysis computer-vision opencv dlib",
    project_urls={
        "Bug Reports": "https://github.com/tu-usuario/face-recognition-analyzer/issues",
        "Source": "https://github.com/tu-usuario/face-recognition-analyzer",
        "Documentation": "https://github.com/tu-usuario/face-recognition-analyzer#readme",
    },
)