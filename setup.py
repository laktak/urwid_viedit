from setuptools import setup
from urwid_viedit import version

setup(
    name="urwid_viedit",
    description="Edit widget supporting vi-mode and emacs keybindings",
    long_description=open("README.rst").read(),
    url="https://github.com/laktak/urwid_viedit",
    version=version,
    author="Christian Zangl",
    author_email="laktak@cdak.net",
    packages=["urwid_viedit"],
    python_requires=">=3.6.0",
    install_requires=["urwid>=1.3.0"],
    license="MIT",
)
