from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
readme = (this_dir / "README.md")
long_description = readme.read_text(encoding="utf-8") if readme.exists() else "speak2py"

setup(
    name="speak2py",
    version="0.3.0",
    description="Stateful natural-language → pandas/matplotlib, offline-first.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Varun Pulipati",
    author_email="varunpulipati26@gmail.com",
    url="https://github.com/varunpuli/speak2py",
    license="MIT",

    package_dir={"": "src"},
    packages=find_packages(where="src", include=["speak2py", "speak2py.*"]),

    install_requires=[
        "pandas>=2.0",
        "matplotlib>=3.6",
        "openpyxl>=3.1",
    ],
    extras_require={
        "local": [],  # (kept empty; AI comes from our embedded server, not llama-cpp)
    },
    entry_points={
        "console_scripts": [
            "s2py = speak2py.cli:main",  # add later if you keep a CLI
        ],
    },
    python_requires=">=3.10",
)
