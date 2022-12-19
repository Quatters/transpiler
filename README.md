# Transpiler

Transpiler from PascalABC.NET to C#. Includes transpiler module which performs
all logic and a simple web interface to interact with.

## Run in docker

To run a docker container with web interface you can use following commands:

```bash
docker build . -t transpiler
docker run -p 8000:8000 --rm transpiler
```

After that you can check [localhost:8000](http://localhost:8000).

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

* Boolean operands must be wrapped into brackets

```pascal
//ok
var b: boolean := (10 < 15) and (5 > 0);

//not supported
var b: boolean := 10 < 15 and 5 > 0;
```

* Comparison of chars and strings are not valid in generated code
```pascal
var c: char := 'c';
var s: string := 'str';

//not valid in generated code
var b: boolean := s = c;
```

* Comparison of strings and chars by `<`, `>`, `<=`, `>=` are not valid in generated code
```pascal
//not valid in generated code
var b: boolean := 'str1' > 'str2';
```

* Number and type of arguments are not checked in function's call

* Base functions are converted by map
```
//example
write() -> Console.Write()
read() -> Console.Read()
```

* Functions that are not contained in map converted with the same name
```
//example
some_function() -> some_function()
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

To run `web` module, install web dependencies first:

```bash
pip install -r requirements-web.txt
```

Then run it with

```bash
python -m web --dev
```

where `--dev` sets uvicorn config suitable for development, e.g. it configures hot reload.

Before submitting a pull request make sure that your code passes
all tests and there are no `flake8` linter errors. Check it with

```bash
python -m unittest
flake8
```

Any new feature must be accompanied by new test for this feature.
