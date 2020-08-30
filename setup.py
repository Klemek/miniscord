import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="miniscord-Klemek",
    version="0.0.1",
    author="Klemek",
    description="A minimalist discord bot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Klemek/miniscord",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
