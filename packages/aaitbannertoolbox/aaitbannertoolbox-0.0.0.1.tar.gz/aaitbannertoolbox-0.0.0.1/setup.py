from setuptools import setup, find_packages
# Configuration
NAME = "aaitbannertoolbox"
VERSION = "0.0.0.1"

INSTALL_REQUIRES = [

]

AUTHOR = ""
AUTHOR_EMAIL = ""
URL = ""
DESCRIPTION = ""
LICENSE = ""
KEYWORDS = ["orange3 add-on",]

PACKAGES = find_packages()
PACKAGES = [pack for pack in PACKAGES if "orangecontrib" in pack]
PACKAGES.append("orangecontrib")
print("####", PACKAGES)

PACKAGE_DATA = {
    "orangecontrib.TOOLBOX.widgets": ["icons/*", "designer/*"]
}

ENTRY_POINTS = {
    "orange.widgets": (
        "AAIT - TOOLBOX = orangecontrib.TOOLBOX.widgets",
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
