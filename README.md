# Transpiler

Transpiler from PascalABC.NET to C#.

## Contribute

Requirements: Python 3.10 or above.

Create, activate virtual env and install dependencies:

```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Run `transpiler` module with

```
python -m transpiler path/to/source/code
e.g.
python -m transpiler examples/supported_syntax.pas
```

Before submitting a pull request make sure that your code passes
all tests and there are no `flake8` linter errors. Check it with

```
python -m unittest
flake8
```
