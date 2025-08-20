from setuptools import setup, find_packages

setup(
    name="doccsy",
    version="1.0",
    description="Generate GitBook-ready Markdown docs from code comments in Lua, JavaScript, and PHP files.",
    author="No-Brainer",
    packages=find_packages(),
    install_requires=[
        "typer",
        "requests",
        "questionary"
    ],
    entry_points={
        "console_scripts": ["doccsy=doccsy.doccsy:app"]
    },
)