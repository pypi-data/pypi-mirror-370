from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bubbleid', # name of packe which will be package dir below project
    version='0.0.9',
    url='https://github.com/cldunlap73/BubbleID',
    author='cldunlap',
    author_email='christydunlap26@gmail.com',
    description='BubbleID Framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    license="Apache-2.0",
    classifiers=[
        'License :: OSI Approved :: Apache Software License'
    ]
)