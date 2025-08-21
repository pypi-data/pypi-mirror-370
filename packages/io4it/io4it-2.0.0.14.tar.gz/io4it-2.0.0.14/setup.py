from setuptools import setup, find_packages

# Configuration
NAME = "io4it"
VERSION = "2.0.0.14"

INSTALL_REQUIRES = [
    "pylatexenc",
    "docopt",
    "boto3",
    "opencv-python-headless==4.6.0.66",
    "docling==2.30.0",
    "docling-core==2.26.3", 
    "speechbrain",
    "whisper",
    "whisper-openai",
    "pyannote.audio",
    "pyannote-core",
    "pypandoc",
    "pypandoc-binary",
    "scikit-learn",
    "openai",
    "pip-system-certs==5.0",
    "docx2pdf",
    "doc2docx",
    "msal",
    "exchangelib"
]

AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = ""
LICENSE = ""
KEYWORDS = ["orange3 add-on",]

PACKAGES = find_packages()
PACKAGES = [pack for pack in PACKAGES if "orangecontrib" in pack and "IO4IT" in pack]
PACKAGES.append("orangecontrib")

PACKAGE_DATA = {
    "orangecontrib.IO4IT.widgets": ["icons/*", "designer/*"],
}


ENTRY_POINTS = {
    "orange.widgets": (
        "Advanced Artificial Intelligence Tools = orangecontrib.IO4IT.widgets",
    )
}

NAMESPACE_PACKAGES = ["orangecontrib"]


setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    keywords=KEYWORDS,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    namespace_packages=NAMESPACE_PACKAGES,
)
