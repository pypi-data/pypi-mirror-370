from setuptools import find_packages, setup

setup(
    name="sclogging",
    version="1.0.6",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={"sclogging": ["config.py", "settings.toml"]},
    url="https://github.com/sshimek42/sclogging",
    license="MIT",
    author="",
    author_email="",
    description="",
)
