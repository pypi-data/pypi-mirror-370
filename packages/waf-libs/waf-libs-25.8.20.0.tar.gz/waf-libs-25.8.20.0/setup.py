"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import pathlib
from codecs import open

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

with open(pathlib.Path(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="waf-libs",
    version=open(pathlib.Path(here, "source", "waflibs", "VERSION")).read().strip(),
    description="waf libs",
    long_description=long_description,
    url="https://bitbucket.org/waf/waflibs",
    author="Felix Wong",
    author_email="felix@waf.hk",
    license="Apache",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="waf-lib waf-libs waf libs waflibs lib waflib",
    packages=find_packages("source"),
    package_dir={"": "source"},
    install_requires=pathlib.Path(here, "requirements.txt")
    .read_text(encoding="utf-8")
    .splitlines(),
    extras_require={
        "test": ["unittest", "nose"],
    },
    test_suite="nose2.collector.collector",
    include_package_data=True,
    package_data={
        "": [
            "VERSION",
        ]
    },
)
