from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.readlines()


setup(
    name='parseltongue',
    version='0.0.1',
    py_modules=['parseltongue'],
    author="Mark Steve Samson",
    author_email="hello@marksteve.com",
    url='https://github.com/marksteve/parseltongue',
    description="Render HTML pages using Markdown and Jinja",
    license="MIT",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'parseltongue=parseltongue:main'
            ]
        },
    )
