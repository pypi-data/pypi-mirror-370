from pathlib import Path

from setuptools import find_packages, setup

import easys_ordermanager


def read_file(filename):
    with (Path(__file__).parent / filename).open(mode="r", encoding="utf-8") as f:
        return f.read()


setup(
    name=easys_ordermanager.__title__,
    packages=find_packages(),
    version=easys_ordermanager.__version__,
    description=easys_ordermanager.__description__,
    author=easys_ordermanager.__author__,
    author_email=easys_ordermanager.__author_email__,
    long_description=(
        read_file("README.md") + "\n\n" + read_file("CHANGELOG.md") + "\n\n" + read_file("CHANGELOG_SERIALIZER.md")
    ),
    long_description_content_type="text/markdown",
    install_requires=[
        "django>=4.2,<6.0",
        "django-countries>=6.0,<8.0",
        "django-internationalflavor>=0.4.0,<0.5.0",
        "django-model-utils>=3.1.2,<6.0.0",
        "django-phonenumber-field>=3.0.1,<9.0",
        "djangorestframework>=3.14,<3.17",
        "idna>=3.10,<4.0",
        "phonenumbers>=8.12.50,<10.0",
    ],
    license=easys_ordermanager.__license__,
    url=easys_ordermanager.__url__,
    download_url="",
    keywords=[],
    include_package_data=True,
    classifiers=[],
)
