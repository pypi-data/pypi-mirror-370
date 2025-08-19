# coding: utf-8
from os.path import (
    dirname,
    join,
)

from setuptools import (
    find_packages,
    setup,
)


def read(file_name):
    with open(join(dirname(__file__), file_name)) as f:
        return f.read()


setup(
    name='m3-registry',
    version='2.3.2',
    url='https://bitbucket.org/barsgroup/registry',
    license='MIT',
    author='BARS Group',
    author_email='bars@bars-open.ru',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description=read('DESCRIPTION.rst'),
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    install_requires=(
        'm3-django-compat>=1.5.1',
        'six >= 1.10.0',
    ),
    include_package_data=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
    ],
)
