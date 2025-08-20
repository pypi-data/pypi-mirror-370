from setuptools import setup, find_packages

setup(
    name='sds_toolbox',
    version='0.0.6',
    description="A complete toolbox to interact with the SDS",
    author='Erwan Le Nagard',
    author_email='erwan@opsci.ai',
    licence="MIT",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "pydantic",
        "pydantic-settings",
        'pandas',
        'humanize'
    ],
)
