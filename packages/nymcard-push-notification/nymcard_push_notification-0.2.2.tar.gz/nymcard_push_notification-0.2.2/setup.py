from os import path

from setuptools import find_packages, setup

NAME = "nymcard-push-notification"
VERSION = "0.2.2"

REQUIRES = ["aiohttp", "django", "djangorestframework", "asgiref"]


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description="Nymcard Push Notification",
    author_email="hello@nuclearo.com",
    author="NymCard BNPL Team",
    license="MIT",
    url="",
    keywords=["Nymcard", "Push Notification"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
