from setuptools import setup, find_packages

setup(
    name="musicgen_trainer",
    version="1.0.0",
    description="A module for advanced music generation and synthesis.",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/musicgen_trainer",
    packages=find_packages(include=["musicgen_trainer", "musicgen_trainer.*"]),
    install_requires=[
        "torch",
        "numpy",
        "music21"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)