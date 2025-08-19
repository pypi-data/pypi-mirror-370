"""
Setup script for emailer-simple-tool package.
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'Readme.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from package
def get_version():
    version_file = os.path.join('src', 'emailer_simple_tool', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '4.1.0'

setup(
    name='emailer-simple-tool',
    version=get_version(),
    author='INAO Team',
    author_email='contact@inao.org',
    description='A personalized email campaign management tool',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/delhomaws/emailer-simple-tool',
    
    # Package configuration
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    
    # Dependencies
    install_requires=[
        'cryptography>=3.4.8',
        'click>=8.0.0',
        'Pillow>=8.0.0',
        'python-docx>=0.8.11',
    ],
    
    # Optional dependencies
    extras_require={
        'gui': [
            'PySide6>=6.0.0',
        ],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
            'mypy>=0.910',
        ],
        'all': [
            'PySide6>=6.0.0',
            'pytest>=6.0.0',
            'pytest-cov>=2.12.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
            'mypy>=0.910',
        ],
    },
    
    # Entry points
    entry_points={
        'console_scripts': [
            'emailer-simple-tool=emailer_simple_tool.cli:main',
        ],
    },
    
    # Classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business',
        'Topic :: Software Development :: User Interfaces',
    ],
    
    # Python version requirement
    python_requires='>=3.8',
    
    # Include additional files
    include_package_data=True,
    zip_safe=False,
)
