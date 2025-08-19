from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    changelog = fh.read()

setup(
    name="minispark",
    version="0.1.10",
    author="段福",
    author_email="duanfu456@163.com",
    description="一个轻量级的Python库，用于从多种数据源读取数据并在本地进行高效处理，类似于Apache Spark的功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/duanfu456/minispark",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3.0",
        "sqlalchemy>=1.4.0",
        "toml>=0.10.2",
        "swifter>=1.0.0",
        "loguru>=0.5.0"
    ],
    extras_require={
        "mysql": ["pymysql>=1.0.0"],
        "duckdb": ["duckdb>=0.3.0"],
        "excel": ["openpyxl>=3.0.0", "xlrd>=2.0.0"],
        "clickhouse": ["clickhouse-driver>=0.2.0"]
    },
    entry_points={
        "console_scripts": [
            "minispark=minispark.cli:main"
        ],
    },
    include_package_data=True,
    package_data={
        "minispark": ["config.toml", "LICENSE"],
    },
)