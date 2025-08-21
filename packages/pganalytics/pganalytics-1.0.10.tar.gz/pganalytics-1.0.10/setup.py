from setuptools import setup, find_packages

setup(
    name="pganalytics",
    version="1.0.10",
    author="pgcass",
    author_email="cansin@pronetgaming.com",
    description="A Python library for analyzing PG data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(include=["pganalytics", "pganalytics.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "google-cloud-bigquery==3.31.0",
        "xgboost",
        "scikit-learn",
        "pyyaml",
        "google-generativeai==0.8.4",
        "db-dtypes",
        "xlsxwriter",
        "pendulum",
        "sqlalchemy>=2.0,<3.0",
        "psycopg2-binary==2.9.10"
    ],
)