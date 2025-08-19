import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'filum_analytics'))

VERSION = "0.1.58"
DESCRIPTION = "Filum Utils"
LONG_DESCRIPTION = "Filum Utils"

install_requires = [
    "requests==2.31.0",
    "sentry-sdk[fastapi]==1.30.0",
    "filum-analytics-python==1.1.1",
    "glom==20.11.0",
    "pyexcel==0.7.0",
    "pyexcel-xls==0.7.0",
    "pyexcel-xlsx==0.6.0",
    "openpyxl==3.0.10",
    "setuptools==68.0.0",
    "tenacity==8.2.3",
    "python-dateutil>=2.8.1",
    "google-cloud-pubsub==2.13.6",
    "google-cloud-storage==2.5.0"
]

setup(
    name="filum-utils",
    version=VERSION,
    author="Hiep Nguyen",
    author_email="<hnguyen@filum.ai>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
