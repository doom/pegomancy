import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pegomancy",
    version="1.1.0",
    author="Clément Doumergue",
    author_email="clement.doumergue@epitech.eu",
    description="Yet another parsing thingy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doom/pegomancy",
    scripts=["pegomant"],
    packages=["pegomancy"],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
