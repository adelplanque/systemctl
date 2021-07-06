from setuptools import setup

setup(
    name="servicectl",
    version="0.1",
    packages=("servicectl", ),
    install_requires=(
        "inotify",
    )
)
