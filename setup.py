import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__VERSION__ = '0.1.8'

ENTRY_POINTS = '''
        [console_scripts]
        readtagger=readtagger.readtagger:main
        allow_dovetailing=readtagger.allow_dovetailing:main
'''

requirements = ['contextlib2', 'pysam', 'six']

if sys.version_info[0] == 2:
    requirements.append('shutilwhich')

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='readtagger',
    version=__VERSION__,
    packages=['readtagger'],
    description="Tags reads in a BAM file based on other BAM files.",
    long_description=readme + '\n\n' + history,
    install_requires=requirements,
    entry_points=ENTRY_POINTS,
    keywords='Bioinformatics',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    extras_require={
        'testing': ["pytest", "pytest-datadir", "tox", "planemo", "cookiecutter", "bumpversion"],
    },
    url='https://github.com/bardin-lab/readtagger',
    license='MIT',
    author='Marius van den Beek',
    author_email='m.vandenbeek@gmail.com',
)
