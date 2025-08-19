# setup.py
from setuptools import setup, find_packages

setup(
    name='brpostagger',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'tensorflow',
        'numpy',
        'pandas',
        'scikit-learn',
        'openpyxl',
    ],
    description='A part-of-speech tagger using LSTM and word normalization',
    author='Mahmudul Haque Shakir',
    author_email='mahmudulhaqueshakir@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
