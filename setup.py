import re
from setuptools import setup # type: ignore


# Get library version
VERSION_REGEX = re.compile(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', re.M)

version = ''
with open('qualichat/__init__.py') as f:
    version = VERSION_REGEX.search(f.read()).group(1) # type: ignore

if not version:
    raise RuntimeError('version is not set')


# Get README file
readme = ''
with open('README.md') as f:
    readme = f.read()


# Get requeirements
requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='qualichat',
    author='Erneist Manhein',
    project_urls={
        'Documentation': 'https://qualichat.readthedocs.io/en/latest/',
        'Issue tracker': 'https://github.com/qualichat/qualichat/issues',
    },
    version=version,
    packages=['qualichat'],
    license='MIT',
    description="Groups' frames of relevance",
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=requirements,
    python_requires='>=3.7.1',
    package_dir={'qualichat': 'qualichat'},
    package_data={
        'qualichat': ['books.txt'],
        '': ['fonts/*.ttf']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ]
)

