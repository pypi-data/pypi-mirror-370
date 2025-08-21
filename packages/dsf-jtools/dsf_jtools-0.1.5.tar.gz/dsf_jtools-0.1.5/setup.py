# setup.py
from setuptools import setup, find_packages
from jtools import __name__, __version__

setup(
    name="dsf-" + __name__,
    version=__version__,
    author='DSFish',
    author_email='liumingshuo1017@gmail.com',
    description='A simple tools module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/DataScienceFish/jtools',
    packages=find_packages(),
    package_data={
        'jtools': ['data/*.csv'],  # 包含 jtools/data 文件夹中的所有 CSV 文件
    },
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9.12',
)