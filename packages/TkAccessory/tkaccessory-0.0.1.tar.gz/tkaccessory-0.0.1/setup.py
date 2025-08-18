from setuptools import setup , find_packages

with open("README.md","r") as file:
    readme = file.read()

setup(
    name="TkAccessory",
    version="0.0.1",
    author="Seyed Moied Seyedi (Single Star)",
    packages=find_packages(),
    install_requires=[
        "customtkinter"
    ],
    license="MIT",
    description="GUI Tool kit",
    long_description=readme,
    long_description_content_type="text/markdown"
)