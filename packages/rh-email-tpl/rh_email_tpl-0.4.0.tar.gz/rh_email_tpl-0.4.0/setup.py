import re
from pathlib import Path

from setuptools import find_namespace_packages, setup


def get_version(*file_paths):
    """Retrieves the version from the given path"""
    filename = Path(__file__).parent.joinpath(*file_paths)
    with filename.open(encoding="utf-8") as f:
        version_file = f.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.MULTILINE,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def long_description():
    """Return long description from README.md if it's present
    because it doesn't get installed."""
    try:
        with Path(Path(__file__).parent, "README.md").open(encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


setup(
    name="rh_email_tpl",
    packages=find_namespace_packages(exclude=["example*"]),
    version=get_version("rh_email_tpl", "__init__.py"),
    description="Internal RegioHelden tool for building styled html emails",
    author="RegioHelden <entwicklung@regiohelden.de>",
    author_email="entwicklung@regiohelden.de",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    install_requires=[
        "Django>=5.1",
        "premailer>=3.10.0",
    ],
    license="MIT",
    keywords=[],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
)
