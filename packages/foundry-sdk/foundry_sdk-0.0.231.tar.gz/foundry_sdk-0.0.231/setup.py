from setuptools import find_packages, setup

# All configuration is now in pyproject.toml
# This setup.py is kept for compatibility
setup(
    packages=find_packages(),
    package_dir={"": "."},
)
