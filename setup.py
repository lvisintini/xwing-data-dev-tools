from setuptools import setup

# Read in the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='XwingDataDevTools',
    version='0.0.1',
    install_requires=requirements,
    author='Luis Visintini',
    author_email='lvisintini@gmail.com',
    packages=['XwingDataDevTools', ],
    url='https://github.com/lvisintini/xwing-data-dev-tools',
    license='The MIT License (MIT)',
    description='A collection of tools used to normalise and improve the xwing-data',
)