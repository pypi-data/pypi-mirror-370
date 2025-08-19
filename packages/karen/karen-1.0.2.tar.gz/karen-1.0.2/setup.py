from setuptools import setup, find_packages
import pathlib

setup (
    name = "karen",
    version = "1.0.2",
    url = "https://github.com/EvilDuck14/Karen/",
    author = "EvilDuck",
    author_email = "theevilduck14@gmail.com",

    packages = find_packages(),
    install_requires = [],
    setup_requires=['setuptools-git'],

    description = "Evaluates & categorises Spider-Man's combos in Marvel Rivals.",
    long_description = (pathlib.Path(__file__).parent.resolve() / "README.md").read_text(encoding="utf-8"),
    long_description_content_type = "text/markdown",

    project_urls={
        "Discord" : "https://discord.gg/RpQf2zVAMP",
        "Source" : "https://github.com/EvilDuck14/Karen/",
    },
)