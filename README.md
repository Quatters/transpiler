# Transpiler

Transpiler from PascalABC.NET to C#.

## Known issues

* Operational assignments are not supported.

```pascal
// ok
var a: integer := 10;
a := a + 1;

// not supported
var a: integer := 10;
a += 1;
```

* Type hints in variable definitions are always required:

```pascal
// ok
var a: char := 'a';

// not supported
var a := 'a';
```

* Inline nested `for`, `while` and `if` statements are not supported

```pascal
// ok
if true then
begin 
    if true then
        print('str');
end;

// not supported
if true then
    if true then
        print('str');
```

## Contribute

Requirements: Python 3.10 or above.

Create, activate virtual env and install dependencies:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

It's recommended to set log level to `DEBUG` when testing. Use

```bash
export LOG_LEVEL=DEBUG
```

before running any of the command below.

Run `transpiler` module with

```bash
python -m transpiler path/to/source/code
```

e.g.

```bash
python -m transpiler examples/supported_syntax.pas
```

Before submitting a pull request make sure that your code passes
all tests and there are no `flake8` linter errors. Check it with

```bash
python -m unittest
flake8
```

Any new feature must be accompanied by new test for this feature.
