from setuptools import setup, find_packages

setup(
    name="astrafy_airflow_utils",
    version="1.2.8",
    packages=find_packages(),
    install_requires=[],
    author="Andrea Bombino",
    description="Astrafy Airflow utils packag3",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/python-packages3/airflow-utils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)