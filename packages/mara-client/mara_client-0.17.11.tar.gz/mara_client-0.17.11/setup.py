from setuptools import find_packages, setup
from pathlib import Path

# for typing
__version__ = "0.0.0"
exec(open("../mara/version.py").read())

# read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="mara_client",
    version=__version__,
    description="A client for the MARA conversational agent for cheminformatics.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Sam Hessenauer, Alex McNerney, Mike Rosengrant",
    author_email="sam@nanome.ai, alex@nanome.ai, mike.rosengrant@nanome.ai",
    url="https://nanome.ai/mara",
    license="",
    packages=find_packages(),
    install_requires=[
        'requests==2.31.0',
        'pandas==2.1.4',
        'pydantic==2.7.3',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
