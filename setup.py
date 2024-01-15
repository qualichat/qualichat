import re
import subprocess
import sys
import platform
from setuptools import setup, Command
from setuptools.command.install import install

# Get library version
VERSION_REGEX = re.compile(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', re.M)

version = ''
with open('qualichat/__init__.py') as f:
    version = VERSION_REGEX.search(f.read()).group(1)
if not version:
    raise RuntimeError('version is not set')

# Get README file
with open('README.md') as f:
    readme = f.read()

# Get requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# class PostInstallCommand(install):
#     """Post-installation for installation mode."""
#     def run(self):
#         install.run(self)
#         subprocess.run(["pip", "install", "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz"])

class CheckVisualStudioCommand(Command):
    description = 'Verifica se o Visual Studio C++ 2019 está instalado'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform.system() == 'Windows':
            # Checking Visual Studio C++ is installed
            try:
                subprocess.check_output(['cl'], stderr=subprocess.STDOUT)
                print("O Visual Studio C++ 2019 está instalado!")
            except FileNotFoundError:
                print("O Visual Studio C++ 2019 não está instalado.")
                print("Para usar este projeto, você precisa instalar o Visual Studio C++ 2019 com a opção 'Desenvolvimento para desktop com C++'.")
                print("Você pode encontrar o Visual Studio C++ 2019 no site oficial da Microsoft: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
                sys.exit(1)

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
        'qualichat': ['books.txt', "connector.csv"],
        '': ['fonts/*.ttf', 'resources/en_core_web_sm-3.7.1.tar.gz']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
    cmdclass={
        # 'install': PostInstallCommand,
        'check_visualstudio': CheckVisualStudioCommand,
    },
)
