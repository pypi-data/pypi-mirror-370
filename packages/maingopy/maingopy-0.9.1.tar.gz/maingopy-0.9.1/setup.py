import re
from setuptools import find_packages
from skbuild import setup


with open('maingopy/Readme.md', 'r') as fh:
    long_description = fh.read()


with open('cmake/MAiNGOversion.cmake', 'r') as versionFile:
    lines = versionFile.readlines()
    MAiNGOversion = lines[1].rstrip()
    p = re.compile(r"^[0-9]\.[0-9]\.[0-9](\.[0-9])?$")
    if not(p.match(MAiNGOversion)):
        raise ValueError("Error reading MAiNGO version. Found invalid string {}".format(MAiNGOversion))


def exclude_static_libraries(cmake_manifest):
    return list(filter(lambda name: not (name.endswith('.a')) and not (name.endswith('.lib')), cmake_manifest))


setup(
    name='maingopy',
    version=MAiNGOversion,
    author='Dominik Bongartz, Jaromil Najman, Susanne Sass, Clara Witte, Alexander Mitsos',
    author_email='MAiNGO@avt.rwth-aachen.de',
    description='A Python package for using MAiNGO - McCormick-based Algorithm for mixed-integer Nonlinear Global Optimization',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='http://permalink.avt.rwth-aachen.de/?id=729717',
    project_urls={
        'Source': 'https://git.rwth-aachen.de/avt-svt/public/maingo',
        'Tracker': 'https://git.rwth-aachen.de/avt-svt/public/maingo/-/issues',
        'Documentation': 'https://avt-svt.pages.rwth-aachen.de/public/maingo',
    },
    license='EPL-2.0',
    packages=['maingopy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)',
        'Programming Language :: C++',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
    ],
    keywords=['optimization','global','nonlinear programming','mixed integer','NLP','MINLP','MAiNGO'],
    cmake_languages=['CXX','C','Fortran'],
    cmake_minimum_required_version='3.19',
    cmake_install_dir='maingopy',
    cmake_process_manifest_hook=exclude_static_libraries,
)