from setuptools import setup, find_packages

# Read the contents of your README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # === Essential Package Information ===
    name='elyzo',
    version='0.1.16',
    packages=find_packages(),

    # === Metadata for PyPI ===
    author='Adrian',
    author_email='adrian@elyzo.ai',
    description='A CLI tool for interacting with the Elyzo platform.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/adrianmm12/elyzo-cli',
    license='MIT',

    # === Dependencies ===
    install_requires=[
        'toml',
        'requests'
    ],
    python_requires='>=3.7', # Specify compatible Python versions

    # === Command-Line Entry Point ===
    entry_points={
        'console_scripts': [
            'elyzo=elyzo.cli:main',
        ],
    },

    # === Classifiers for categorizing the package ===
    # Full list: https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)