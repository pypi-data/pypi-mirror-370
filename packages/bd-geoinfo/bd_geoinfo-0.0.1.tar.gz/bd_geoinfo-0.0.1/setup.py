from setuptools import setup, find_packages
import os

def read_requirements():
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', encoding='utf-8') as req_file:
            return req_file.read().splitlines()
    return []

def read_readme():
    if os.path.exists('README.md'):
        with open('README.md', encoding='utf-8') as readme_file:
            return readme_file.read()
    return ""

setup(
    name='bd-geoinfo',
    version='0.0.1',
    author='Asaduzzaman Asad',
    author_email='zyxmdasaduzzaman@gmail.com',
    description='A simple Python library for fetching geographical information about Bangladesh.',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/zyxasaduzzaman/BD_GEOINFO',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: GIS',
        'Development Status :: 3 - Alpha',
        'Natural Language :: Bengali',
        'Natural Language :: English'
    ],
    install_requires=read_requirements(),
    python_requires='>=3.6',
    include_package_data=True,
)