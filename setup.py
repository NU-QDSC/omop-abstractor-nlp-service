from setuptools import setup, find_packages

ABOUT = {}
with open("textabstractor/about.py", "r") as about_file:
    exec(about_file.read(), ABOUT)

setup(
    name=ABOUT["__project_name__"],
    version=ABOUT["__version__"],
    author="Will Thompson",
    maintainer="Will Thompson",
    description="NLP web service code for the OMOP Abstractor",
    packages=find_packages(
        include=[
            "textabstractor",
            "textabstractor.*",
            "textabstractor_testdata",
            "textabstractor_testdata.*",
            "textabstractor_testdata.breast.*",
            "textabstractor_testdata.prostate.*",
        ]
    ),
    package_data={"": ["*.json"]},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "fastapi[all]",
        "celery[redis]",
        "typer[all]",
        "uvicorn",
        "requests",
        "pluggy",
        "importlib_resources",
        "rich",
        "httptools",
        "tinydb",
        "flower"
    ],
    extras_require={
        "interactive": ["jupyterlab", "rise"],
        "dev": [
            "black",
            "pyment",
            "twine",
            "tox",
            "bumpversion",
            "flake8",
            "coverage",
            "sphinx",
        ],
        "test": ["pytest", "starlette"],
    },
)
