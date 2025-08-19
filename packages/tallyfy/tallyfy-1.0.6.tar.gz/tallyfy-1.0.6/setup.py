"""
Setup script for Tallyfy SDK
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Read version from __init__.py
def get_version():
    version_file = os.path.join(this_directory, 'tallyfy', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.0.6'

setup(
    name='tallyfy',
    version=get_version(),
    author='Tallyfy',
    author_email='support@tallyfy.com',
    description='A comprehensive Python SDK for interacting with the Tallyfy API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tallyfy/tallyfy-sdk',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    python_requires='>=3.7',
    install_requires=[
        'requests>=2.25.0',
        'typing-extensions>=4.0.0; python_version<"3.8"',
        "email-validator==2.2.0",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'mypy>=0.800',
        ],
    },
    keywords='tallyfy api sdk workflow automation task management',
    project_urls={
        'Documentation': 'https://tallyfy.com/products/',
        'Source': 'https://github.com/tallyfy/sdk',
        'Tracker': 'https://github.com/tallyfy/sdk/issues',
    },
    include_package_data=True,
    zip_safe=False,
)