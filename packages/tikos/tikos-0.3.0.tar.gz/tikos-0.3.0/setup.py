import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="tikos",
    version="0.3.0",
    author="Don Liyanage, Tikos Technologies Ltd",
    author_email="don.liyanage@tikos.tech",
    description=("Tikos Platform Library"),
    license="Apache-2.0",
    keywords="Tikos",
    url="http://packages.python.org/tikos",
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description_content_type="text/markdown",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
    ],
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            "tikos=tikos:Description",
        ]
    },
)
