"""
Setup script for the FlowKit package
"""
from setuptools import setup, find_packages

# read in version string
VERSION_FILE = 'flowkit/_version.py'
__version__ = None  # to avoid inspection warning and check if __version__ was loaded
exec(open(VERSION_FILE).read())

if __version__ is None:
    raise RuntimeError("__version__ string not found in file %s" % VERSION_FILE)

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

reqs = [
    'anytree>=2.6',
    'bokeh>=2.4,<3',
    'flowio==1.1.1',
    'flowutils>=1,<1.1',
    'lxml>=4.7',
    'matplotlib>=3.5',
    'networkx>=2.3',
    'numpy>=1.20',
    'pandas>=1.2,<2',
    'psutil>=5.8',
    'scipy>=1.6',
    # 'seaborn>=0.11,<0.12' # REMOVING THIS AS WE'RE NOT USING IT
]

setup(
    name='FlowKit',
    version=__version__,
    packages=find_packages(exclude=["flowkit/tests/"]),
    package_data={'': ['_resources/*.xsd']},
    include_package_data=True,
    description='Flow Cytometry Toolkit',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Scott White",
    license='BSD',
    url="https://github.com/whitews/flowkit",
    ext_modules=[],
    install_requires=reqs,
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7'
    ]
)
