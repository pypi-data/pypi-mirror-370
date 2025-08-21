from setuptools import setup, find_packages

setup(
    name='spyrgedb',
    version='0.0.1',
    description='A Python library to interact with SborgDB API.',
    author='abdullah',
    author_email='*@spyrgedb.com',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)