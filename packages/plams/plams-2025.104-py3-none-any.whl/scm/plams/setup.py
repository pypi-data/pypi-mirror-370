from setuptools import find_packages, setup

# This minimal setup.py exists alongside the pyproject.toml for legacy reasons.
# Currently, the "artificial" prefix "scm.plams" is added to the (sub)package names, which is not supported via the pyproject.toml.
# ToDo: the package should be restructured with a directory structure that reflects this, then the setuptools package finding used.
# See: https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
setup(
    packages=["scm.plams"] + ["scm.plams." + i for i in find_packages(".")],
    package_dir={"scm.plams": "."},
    package_data={
        "scm.plams": [
            ".flake8",
            "examples/*",
            "examples/**/*",
            "unit_tests/*",
            "unit_tests/**/*",
        ]
    },
)
