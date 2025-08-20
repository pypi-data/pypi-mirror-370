from setuptools import setup, find_packages

requirements = [
    "click",
    "rich",
    "boto3",
    "questionary",
    "configparser"
]
setup(
    name='pdcli-inf',
    version='1.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pdcli-inf=pd_cli.cli:cli',
        ],
    },
)