from setuptools import setup
import pathlib

VERSION = '0.1.0'

# The directory containing this file
HERE = pathlib.Path(__file__).resolve().parent

# The text of the README file is used as a description
README = HERE.joinpath("README.md").read_text()

setup(
    name='IEEE LDPC',
    version=VERSION,
    packages=['code_specs', 'ldpc'],
    url='https://github.com/YairMZ/belief_propagation',
    license='MIT',
    author='Yair Mazal',
    author_email='yairmazal@gmail.com',
    description='Belief propagation on Tanner graphs. Implements an LLR based LDPC decoder.',
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering"
        ],
    include_package_data=True,
    install_requires=["numpy", "networkx"],
    keywords=["LDPC", "Belief Propagation", "SPA", "Tanner Graph"]
)
