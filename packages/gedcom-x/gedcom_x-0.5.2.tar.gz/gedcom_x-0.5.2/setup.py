# setup.py
from setuptools import setup, find_packages

setup(
    name='gedcom-x',
    version='0.5.2',
    packages=find_packages(),
    install_requires=[
        # List your project dependencies here, e.g.,
        'ged4py',
    ],
    entry_points={
        'console_scripts': [
            # Define command-line scripts if needed
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)