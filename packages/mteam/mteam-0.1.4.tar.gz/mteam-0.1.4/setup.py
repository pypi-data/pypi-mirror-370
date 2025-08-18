from setuptools import setup, find_packages

setup(
    name="mteam",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "httpx>=0.22.0",
        "pydantic~=1.10.22",
        "python-dotenv>=0.19.0",
    ],
) 