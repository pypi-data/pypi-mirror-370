from setuptools import setup, find_packages
import pathlib

# Read README.md for long description
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ur-aj",
    version="0.1.3",
    description="Python library for controlling Universal Robots via sockets",
    long_description=long_description,                # <-- Added
    long_description_content_type="text/markdown",    # <-- Important for PyPI
    author="Akshay Ajit Bhawar",
    author_email="akshayfusion1@gmail.com",
    url="https://github.com/Akshaybhawarkiti/UR-aj",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
