from setuptools import setup, find_packages
from os import path

HERE = path.abspath(
    path.dirname(__file__)
)

ROOT_PACKAGE = 'convisoappsec'
SCRIPTS_SHELL_COMPLETER_DIR = path.join('scripts', 'shell_completer')
VERSION_MODULE = path.join(ROOT_PACKAGE, 'version.py')
README_PATH = path.join(HERE, 'README.md')

version_module_context = {}


with open(VERSION_MODULE) as fp:
    exec(fp.read(), version_module_context)

with open(README_PATH, "r") as fh:
    long_description = fh.read()

version = version_module_context.get('__version__')

setup(
    name='conviso-cli',
    version=version,
    long_description=long_description,
    long_description_content_type='text/markdown',
    maintainer='Conviso',
    maintainer_email='development@convisoappsec.com',
    package_data={'convisoappsec': ['flowcli/vulnerability/rules_schema.json']},
    packages=find_packages(
        exclude=["test*"],
    ),
    install_requires=[
        "GitPython==3.1.45",
        "click==8.1.8",
        "requests==2.32.3",
        "urllib3==2.4.0",
        "semantic-version==2.10.0",
        "docker==7.1.0",
        "PyYAML==6.0.2",
        "click-log==0.4.0",
        "transitions==0.9.2",
        "jsonschema==4.25.0",
        "giturlparse<=0.12.0",
        "jmespath==1.0.1",
        "setuptools==78.1.0"
    ],
    entry_points={
        'console_scripts': [
            'flow=convisoappsec.flowcli.entrypoint:cli',
            'conviso=convisoappsec.flowcli.entrypoint:cli',
        ]
    },
    scripts=[
        path.join(SCRIPTS_SHELL_COMPLETER_DIR, 'flow_bash_completer.sh'),
        path.join(SCRIPTS_SHELL_COMPLETER_DIR, 'flow_zsh_completer.sh'),
        path.join(SCRIPTS_SHELL_COMPLETER_DIR, 'flow_fish_completer.fish'),
    ],
    project_urls={
        'Source': 'https://github.com/convisoappsec/convisocli/',
    },
    python_requires='>=3.9',
)
