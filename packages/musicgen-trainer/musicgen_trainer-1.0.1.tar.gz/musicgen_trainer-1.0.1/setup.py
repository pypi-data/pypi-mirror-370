from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="musicgen_trainer",
    version="1.0.1",  # Incremented version number
    description="A module for advanced music generation and synthesis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Flana",  # Updated author name
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