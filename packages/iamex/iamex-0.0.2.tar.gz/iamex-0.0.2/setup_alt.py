"""
Configuración de setuptools para iamex
"""

from setuptools import setup, find_packages

with open("README_alt.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="iamex",
    version="0.0.2",
    author="Inteligencia Artificial México",
    author_email="hostmaster@iamex.io",
    description="Acceso unificado a múltiples modelos de inferencia AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IA-Mexico/iamex",
    project_urls={
        "Bug Tracker": "https://github.com/IA-Mexico/iamex/issues",
        "Documentation": "https://github.com/IA-Mexico/iamex#readme",
        "Source Code": "https://github.com/IA-Mexico/iamex",
    },
    package_dir={"": "src_alt"},
    packages=find_packages(where="src_alt"),
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[],  # Sin dependencias para la versión inicial
    keywords="ai, machine learning, inference, models, iamex, artificial intelligence",
)
