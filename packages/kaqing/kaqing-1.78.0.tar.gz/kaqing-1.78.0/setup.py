from setuptools import setup, find_packages

setup(
    name='kaqing',
    version='1.78.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'qing = walker.cli:cli'
        ]
    }
)
