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

Run `pascal2csharp` module with

```
python -m pascal2csharp
```

Before submitting a pull request make sure that your code passes
all tests and there is no `flake8` linter errors. Check it with

```
python -m unittest
flake8
```
