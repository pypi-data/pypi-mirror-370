
from setuptools import setup, find_packages

setup(
    name='sci-kit',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['pandas'],
    author='Ahmad R. Khan',
    author_email='your@email.com',
    description='A utility library by Sci-kit',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
