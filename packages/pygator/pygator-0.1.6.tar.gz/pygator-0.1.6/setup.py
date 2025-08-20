from setuptools import setup, find_packages
import re 

with open("pygator/_version.py", "r") as f:
    version = re.search(r'__version__\s*=\s*"(.+)"', f.read()).group(1)

setup(
    name="pygator",
    version=version,
    packages=find_packages(),   # will find uf_optics and subfolders
    install_requires=[],        # list dependencies if needed
    description="A package for optical utilities",
    author="Raed Diab",
    author_email="contact@raeddiab.com",
    url="https://github.com/DiabRaed/pygator",                     # optional, GitHub repo URL
)