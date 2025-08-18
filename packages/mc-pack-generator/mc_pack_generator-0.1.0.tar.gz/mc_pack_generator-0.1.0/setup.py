import os
from setuptools import setup, find_packages

setup(
    name='mc-pack-generator',
    version='0.1.0',
    author='Seu Nome',
    description='Gerador de pacotes para Minecraft Bedrock (Behavior, Resource, Skin)',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'mc-pack-generator = mc_pack_generator.main:main',
        ],
    },
)