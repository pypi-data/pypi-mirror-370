# ash-cli/setup.py
from setuptools import setup, find_packages

setup(
    name='ash-cli',
    version='2.0.0', 
    author='Raunak', 
    author_email='rs1103307@gmail.com',
    description='Aisha CLI: An interactive AI chat assistant with customizable features.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hacxworld/ash-cli', 
    packages=find_packages(),
    install_requires=[
        'requests',
        'rich', 
        'prompt_toolkit',
    ],
    entry_points={
        'console_scripts': [
            'ash=ash_cli.ash:main', 
        ],
    },
    
    classifiers=[
        'Development Status :: 5 - Production/Stable', 
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License', 
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Communications :: Chat',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Utilities',
    ],
    keywords='ai chat assistant cli gemini',
    python_requires='>=3.8',
)