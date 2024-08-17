from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in party_statement/__init__.py
from party_statement import __version__ as version

setup(
	name="party_statement",
	version=version,
	description="Party Statment Doctypes",
	author="Infinity Systems",
	author_email="info@infinitysys.org",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
