from setuptools import setup, find_packages
# Configuration
NAME = "aaitbannertoolbox"
VERSION = "0.0.0.3"



AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = ""
LICENSE = ""
KEYWORDS = ["orange3 add-on",]

PACKAGES = find_packages(include=["*"])
INSTALL_REQUIRES = [
]
# Définit quels fichiers non-Python embarquer
PACKAGE_DATA = {
    "": [
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg",
        "*.ui", "*.ini", 
    ]
}
ENTRY_POINTS = {
    "orange.widgets": (
        "AAIT Banner Toolbox = orangecontrib.TOOLBOX.widgets",
    ),
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
    include_package_data=True,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    entry_points=ENTRY_POINTS,
    namespace_packages=NAMESPACE_PACKAGES
)
