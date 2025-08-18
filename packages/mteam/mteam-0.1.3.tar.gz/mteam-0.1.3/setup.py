from setuptools import setup, find_packages

setup(
    name="mteam",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
) 