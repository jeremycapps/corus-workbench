from setuptools import find_packages, setup


setup(
    name="corus-workbench",
    version="0.1.0",
    packages=find_packages(".", include=["kernel*", "corus*"]),
    install_requires=[
        "typer",
        "pydantic",
        "pyyaml",
        "httpx",
        "beautifulsoup4",
        "markdownify",
        "duckdb",
        "pandas",
        "geopandas",
        "shapely",
        "pyarrow",
        "rich",
        "jsonschema",
        "python-dotenv",
    ],
    entry_points={"console_scripts": ["corus=kernel.command.cli:app"]},
)
