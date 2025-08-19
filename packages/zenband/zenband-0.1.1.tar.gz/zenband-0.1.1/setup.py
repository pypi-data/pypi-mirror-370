from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()

setup(
    name='zenband',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        "customtkinter",
        'tqdm',
        'imageio',
    ],
    entry_points={
        'console_scripts': [
            'zenband-run = ZenBand:run'
        ],
    },
    long_description=description,
    long_description_content_type='text/markdown',
)