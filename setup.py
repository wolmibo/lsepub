from setuptools import setup
from lsepub.meta import version, name, description

setup(
    name=name,
    version=version,
    description=description,
    url='https://github.com/wolmibo/lsepub',
    license='MIT',
    packages=['lsepub'],
    entry_points=dict(
        console_scripts=['lsepub=lsepub.main:main']
    )
)
