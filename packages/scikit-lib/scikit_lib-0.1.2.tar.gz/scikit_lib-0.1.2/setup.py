
from setuptools import setup, find_packages

setup(
    name='scikit_lib',
    version='0.1.2',
    packages=find_packages(),
    install_requires=['pandas'],
    author='Raymond',
    description='A utility library by Sci-kit',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
