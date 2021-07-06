from setuptools import find_packages
from servicectl.setup import setup


setup(
    name="otherproject",
    packages=find_packages(),
    entry_points={
        "console_scripts": (
            "otherproject.manage = otherproject.djangoapp.manage:main",
        )
    },
    install_requires=(
        "django",
        "gunicorn",
        "jinja2",
        "psycopg2",
    ),
    include_package_data=True
)
