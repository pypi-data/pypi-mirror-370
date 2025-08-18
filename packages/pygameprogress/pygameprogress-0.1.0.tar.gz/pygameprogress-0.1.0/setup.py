from setuptools import setup

setup(
    name='pygameprogress',
    version='0.1.0',
    author='Wilder',
    description='Modular progress bar system for Pygame projects',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/pygameprogress',
    packages=['pygameprogress'],
    package_dir={'pygameprogress': '.'},
    install_requires=[
        'pygame>=2.0.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.7',
    include_package_data=True,
)