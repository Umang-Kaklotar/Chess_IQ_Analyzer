"""
Setup script for Chess IQ Analyzer.
"""

from setuptools import setup, find_packages

setup(
    name="chess_iq_analyzer",
    version="0.1.0",
    description="Chess game with IQ analysis and performance tracking",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "pytest>=7.3.1",
    ],
    entry_points={
        "console_scripts": [
            "chess-iq=main:main",
            "analyze-chess=analyze_chess:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment :: Board Games",
    ],
    python_requires=">=3.8",
)
