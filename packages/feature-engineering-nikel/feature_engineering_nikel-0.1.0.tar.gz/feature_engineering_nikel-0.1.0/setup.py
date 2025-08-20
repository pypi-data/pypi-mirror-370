# setup.py

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'feature_engineering_nikel'
DESCRIPTION = 'A comprehensive and flexible library for feature engineering in Python.'
URL = 'https://github.com/aditnikel/fds-v2-ai-ml/tree/main/services/feature_pipeline'
EMAIL = 'adityano@nikel.com'
AUTHOR = 'Ratu, Adityano W'
REQUIRES_PYTHON = '>=3.9.0'
VERSION = '0.1.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'numpy',
    'pandas',
    'scikit-learn',
    'scipy'
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)