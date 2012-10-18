from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.readlines()


setup(
    name='parseltongue',
    version='0.0.0',
    py_modules=['parseltongue'],
    author="Mark Steve Samson",
    author_email="hello@marksteve.com",
    description="Yet another blog thingy",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'parseltongue=parseltongue:main'
            ]
        },
    )
