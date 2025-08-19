from setuptools import setup, find_packages

setup(
    name="shownamer",
    version="1.3.0",
    author="Amal Lalgi",
    description="Rename TV show Media files with Respective episode Titles/Names.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/theamallalgi/shownamer",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={"console_scripts": ["shownamer = shownamer.cli:main"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
