from setuptools import setup, find_packages

setup(
    name="pygator",
    version="0.1.5",
    packages=find_packages(),   # will find uf_optics and subfolders
    install_requires=[],        # list dependencies if needed
    description="A package for optical utilities",
    author="Raed Diab",
    author_email="contact@raeddiab.com",
    url="https://github.com/DiabRaed/pygator",                     # optional, GitHub repo URL
)