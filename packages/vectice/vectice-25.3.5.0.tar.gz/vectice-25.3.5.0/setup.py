import os
import sys
from ast import parse

from setuptools import setup

if sys.version_info < (3, 9):
    print("vectice requires Python 3 version >= 3.9", file=sys.stderr)
    sys.exit(1)

package_root = os.path.abspath(os.path.dirname(__file__))

version_requires = ">=3.9.0"

with open(os.path.join("src", "vectice", "__version__.py")) as f:
    version = parse(next(line for line in f if line.startswith("__version__"))).body[0].value.s

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name="vectice",
    version=version,
    description="Vectice Python library",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Vectice Inc.",
    author_email="sdk@vectice.com",
    url="https://www.vectice.com",
    package_data={"vectice": ["py.typed"]},
    license="Apache License 2.0",
    keywords=["Vectice", "Client", "API", "Adapter"],
    platforms=["Linux", "MacOS X", "Windows"],
    python_requires=version_requires,
    install_requires=[
        "types-python-dateutil",
        "python-dotenv>=0.11.0",
        "requests<=2.32.4",
        "rich",
        "urllib3<=2.5.0",
        "gql[requests]>=4.0.0",
        "GitPython",
        "matplotlib",
        "packaging",
        "Pillow",
        "pandas",
        "typing-extensions>=4.5.0",  # Prior to 4.6.2 because of colab issues with tensorflow 2.13.0
        "dataclasses-json==0.5.8",
        "IPython",
        "ipynbname",
    ],
    extras_require={
        "dev": [
            "black==24.2.0",
            "gitpython",
            "pyright==1.1.360",
            "ruff",
            "types-requests",
            "types-urllib3",
            "types-mock",
            "mypy_boto3_s3==1.34.65",
            "pandas-stubs",
        ],
        "doc": [
            "black==24.2.0",
            "markdown-callouts>=0.2",
            "markdown-exec>=1.2",
            "mkdocs",
            "mkdocs-material>=7.3",
            "mkdocs-redirects>=1.2",
            "mkdocs-section-index>=0.3",
            "mkdocstrings[python]>=0.18",
        ],
        "test": [
            "docker==7.1.0",
            "docker-compose",
            "dslr[psycopg2-binary]",
            "mock>=1.0.1",
            "numpy",
            "pytest==8.2.0",
            "pytest-randomly",
            "coverage",
            "pytest-cov",
            "pydrive2",
            "scikit-learn<=1.6.1",
            "testcontainers",
            "db-dtypes>=1.1.1",
            "pyspark",
            "mlflow<=2.22.1",
            "Cython>=3.0",
            "pyyaml==5.3.1",
            "pyarrow>=15.0.0; python_version >= '3.12'",
            "IPython",
            "matplotlib",
            "papermill",
            "tenacity==8.3.0",
            "plotly",
            "ipynbname",
            "nbformat",
            "lightgbm",
            "catboost",
            "tensorflow>=2.15.1",
            "keras",
            "snowflake-snowpark-python",
            "seaborn",
            "statsmodels",
            "xgboost",
            "kaleido",
            "torch",
            "ipywidgets",
            "polars",
            "wandb",
        ],
        "gcs": ["google-cloud-storage>=1.17.0", "google-cloud-bigquery", "protobuf"],
        "s3": ["boto3"],
        "validation": ["shap>=0.44.1", "scipy<=1.12"],
    },
    classifiers=[
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
)
