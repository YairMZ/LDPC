from setuptools import setup
import pathlib

VERSION = '0.1.1'

# The directory containing this file
HERE = pathlib.Path(__file__).resolve().parent

# The text of the README file is used as a description
README = HERE.joinpath("README.md").read_text()

setup(
    name='sim-ldpc',
    version=VERSION,
    packages=['ldpc', 'ldpc.utils', 'ldpc.encoder', 'ldpc.decoder'],
    url='https://github.com/YairMZ/LDPC',
    license='MIT',
    author='Yair Mazal',
    author_email='yairmazal@gmail.com',
    description='Simulate LDPC codes, both encoding and decoding',
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        "Topic :: Scientific/Engineering"
        ],
    include_package_data=True,
    install_requires=["numpy", "networkx", "scipy", "bitstring"],
    keywords=["LDPC", "Belief Propagation", "SPA", "Tanner Graph", "IEEE 802.11"]
)
