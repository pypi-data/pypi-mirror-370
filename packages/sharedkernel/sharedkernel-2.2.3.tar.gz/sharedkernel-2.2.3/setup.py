from setuptools import setup

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name="sharedkernel",
    author="Smilinno",
    packages=[
        "sharedkernel",
        "sharedkernel.database",
        "sharedkernel.enum",
        "sharedkernel.exception",
        "sharedkernel.objects",
        "sharedkernel.normalizer",
    ],
    # Needed for dependencies
    install_requires=[
        "numpy",
        "requests",
        "pymongo",
        "fastapi",
        "PyJWT",
        "persian_tools",
        "sentry-sdk",
        "jdatetime",
        "persiantools",
        "boto3==1.35.90",
        "python-docx",
        "mammoth",
        "markdown",
        "beautifulsoup4",
        "deepdiff",
    ],
    # *strongly* suggested for sharing
    version="2.2.3",
    description="sharekernel is a shared package between all python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
