from setuptools import setup, find_packages

setup(
    name="pytensorlite",
    version="0.1.4",  # incrémente bien à chaque rebuild
    packages=find_packages(),
    description="Lightweight tensor utilities for Python AI modules.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sami Haddadi",
    author_email="garnet_smitham18209@vonju.org",
    url="https://github.com/93dk99-ui/pytensorlite",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
)
