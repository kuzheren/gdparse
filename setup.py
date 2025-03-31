from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gdparse",
    version="0.3.0",
    author="kuzheren",
    author_email="kuzherendev@gmail.com",
    description="Simple parser for Geometry Dash levels",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kuzheren/gdparse",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
