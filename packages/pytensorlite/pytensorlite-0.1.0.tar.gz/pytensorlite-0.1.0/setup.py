from setuptools import setup, find_packages

setup(
    name="pytensorlite",
    version="0.1.0",
    packages=find_packages(),
    description="Lightweight tensor utilities for Python AI modules.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Sami Haddadi",
    author_email="sami.haddadi.dev@gmail.com",
    url="https://github.com/samihaddadi/pytensorlite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
)
