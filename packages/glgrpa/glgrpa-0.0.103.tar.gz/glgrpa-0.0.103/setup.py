# setup.py
from setuptools import setup, find_packages

# Leer el archivo README.md con codificación UTF-8
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='glgrpa',
    version='0.0.103',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'selenium',
        'pandas',
        'colorama',
        'openpyxl',
        'office365-rest-python-client',
        'pyautogui',
        'pywinauto',
        'psutil'
    ],
    description='Librería para automatización de tareas en RPA dentro de Grupo Los Grobo',
    author='Bellome, Gabriel <gabriel.bellome@losgrobo.com>',
    author_email='gabriel.bellome@losgrobo.com',
    url='https://GrupoLosGrobo@dev.azure.com/GrupoLosGrobo/GrupoLosGrobo%20RPA/_git/GrupoLosGrobo%20RPA',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)