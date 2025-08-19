# CLI

This is a command line tool to interact with [convisoappsec] API. 

# Documentation
Please visit the [official documentation] for further information.

[official documentation]: <https://docs.convisoappsec.com/cli/installation>

# Development Mode

To run this application in development mode, follow these steps:

## 1. Clone the Repository

First, clone this repository:

```shell
git clone <repository_url>
cd convisocli
```

## Set Up Python Environment
Create and activate a virtual environment:
```shell
  python -m venv venv
  source venv/bin/activate  # On macOS/Linux
  venv\Scripts\activate     # On Windows

```
and then install in development mode:
```shell
    pip install -e .
```

### Using pyenv:

If you don't have pyenv installed, follow the installation guide:
https://github.com/pyenv/pyenv?tab=readme-ov-file#installation

```shell
  pyenv install 3.13.1
```

To set a version only for convisocli, go to convisocli directory and run:
```shell
  pyenv local 3.13.1
```

To set a python version globally:

```shell
    pyenv global 3.13.1
```

and then you can run:
```shell
  pip install -e .
```
To install convisocli.

Run the following command to check if convisocli is installed correctly:

```shell
    conviso --help
```

To run the tests, install the required dependencies by running:

```shell
    pip install -r dev_requirements.txt
```

Once installed, execute the tests with:

```shell
    pytest
```

To run tests with coverage report:

```shell
    pytest --cov=convisoappsec test/
```
