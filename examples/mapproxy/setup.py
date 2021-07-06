from setuptools import find_packages
from servicectl.setup import setup


setup(
    name="myproject",
    packages=find_packages(),
    install_requires=(
        "jinja2",
        "mapproxy",
        "pyproj==1.9.6",
        "redis",
        "uwsgi",
    ),
    include_package_data=True
)
