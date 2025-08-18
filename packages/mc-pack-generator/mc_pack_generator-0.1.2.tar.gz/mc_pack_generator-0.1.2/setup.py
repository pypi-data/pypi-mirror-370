import os
from setuptools import setup, find_packages

# Caminho absoluto do diretório atual
this_directory = os.path.abspath(os.path.dirname(__file__))

# Caminho para o README.md
readme_path = os.path.join(this_directory, "README.md")

# Lê o conteúdo do README.md
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ""

setup(
    name='mc-pack-generator',
    version='0.1.2',
    author='Seu Nome',
    description='Gerador de pacotes para Minecraft Bedrock (Behavior, Resource, Skin)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'mc-pack-generator = mc_pack_generator.main:main',
        ],
    },
)