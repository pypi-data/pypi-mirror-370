from setuptools import find_packages, setup

setup(
    name="dscin_ppy",
    version="0.0.14",
    author="Andrea Chiappo",
    author_email="chiappo.andrea@gmail.com",
    description="Collection of utility functions",
    packages=find_packages(include=["dscin_ppy"]),
    test_suite="tests",
    install_requires=[
        "scipy==1.10.1",
        "pandas==2.0.1",
        "numpy==1.23.5",
        "s3fs==2022.11.0",
        "hdbcli==2.19.21",
        "s3transfer==0.6.1"
    ]
)