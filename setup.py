from setuptools import setup
import os

with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "urwid_viedit", "__init__.py")
) as fd:
    version = [line.split()[-1].strip('"') for line in fd if line.startswith("version")]
if not version:
    raise Exception("Missing version!")

setup(
    name="urwid_viedit",
    description="Edit widget supporting vi-mode and emacs keybindings",
    long_description=open("README.rst").read(),
    url="https://github.com/laktak/urwid_viedit",
    version=version[0],
    author="Christian Zangl",
    author_email="laktak@cdak.net",
    packages=["urwid_viedit"],
    python_requires=">=3.6.0",
    install_requires=["urwid>=1.3.0"],
    license="MIT",
)
