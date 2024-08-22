from setuptools import setup, find_packages

def load_requirements(filename='requirements.txt'):
    with open(filename, 'r') as file:
        return file.read().splitlines()


setup(
    name="All_lib",
    version="0.1",
    author="La Rosa Francesco",
    author_email="francesco.larosa2001.flr@gmail.com",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GoldenRose01/Thesis",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
    install_requires=load_requirements(),
    entry_points={
        'console_scripts': [
            'nome-comando=mio_package.nome_modulo:funzione_principale',
        ],
    },
)
