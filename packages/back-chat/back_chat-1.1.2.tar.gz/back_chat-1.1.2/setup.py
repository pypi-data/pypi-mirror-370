import os

from setuptools import setup, find_packages
from src.back_chat import __version__
import shutil

source_dir = './src'
destination_dir = '.'

shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)

with open('requirements.txt', 'r', encoding='utf-16') as f:
    requirements = [line.strip() for line in f if line.strip()]
with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='back_chat',
    version=__version__,
    author="agrubio",
    author_email="contact@agrubio.dev",
    keywords='development, setup, setuptools',
    python_requires='>=3.12',
    url='https://github.com/AbelGRubio/backend-chat.git',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=['back_chat', 'back_chat.*', '']),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",],
    include_package_data=True,
    package_data={'': [os.path.join("conf", "*"),
                       os.path.join("static", "*")]})
