from setuptools import setup, find_packages

setup(
    name="ur-aj",
    version="0.1.0",
    description="Python library for controlling Universal Robots via sockets",
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
