import time
import warnings
from setuptools import setup, find_packages
import sys
import subprocess
import platform
from setuptools.command.install import install

def log_message(message, level="INFO"):
    timestamp = time.strftime("%H:%M:%S")
    border = "=" * (len(message) + 4)
    print(f"\n{border}")
    print(f"{timestamp} - {level} - {message}")
    print(f"{border}\n")

class CustomInstall(install):
    def run(self):
        log_message(f"Début de l'installation de {NAME} v{VERSION}")
        log_message("Étape 1/2 : Installation des dépendances principales")
        install.run(self)

        if 'cuda' in sys.argv:
            log_message("Option [cuda] détectée", "IMPORTANT")
            log_message("⚠️ Assurez-vous d’utiliser --extra-index-url https://download.pytorch.org/whl/cu126", "NOTE")
        else:
            log_message("Mode CPU sélectionné", "NOTE")
            self._warn_cuda_option()

    def _warn_cuda_option(self):
        if platform.system() == "Windows":
            log_message("ASTUCE: Pour activer CUDA sous Windows", "NOTE")
            print("\033[94m" + "="*80)
            print("Pour une version avec accélération GPU, utilisez :")
            print("pip install io4it[cuda] --extra-index-url https://download.pytorch.org/whl/cu126")
            print("="*80 + "\033[0m\n")

# Configuration
NAME = "io4it"
VERSION = "2.0.0.10"

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
    "CATEGORIT",
    "pip-system-certs"
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
