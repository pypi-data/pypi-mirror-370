# Pybase library

## Build

1. Create more file `.pypirc` file like

```code
[distutils]
index-servers = gitlab

[gitlab]
repository: https://gitlab.gt.vng.vn/api/v4/projects/2968/packages/pypi
username: vanntl
password: glpat-B92yhX******
```

2. Move `.pypirc` file to your home directory
```bash
cp .pypirc ~/
```

3. Build
- Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m build
python -m twine upload dist/*
```

- Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m build
python -m twine upload dist/*
```

## How to install

1. Create more `.netrc` file like
```txt
machine gitlab.gt.vng.vn
login your-token-name
password your-token-value
```

2. Copy .netrc file to your home directory
```bash
cp .netrc ~/

```

- Linux
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py sdist bdist_wheel
```

## How to install

1. Create more `.netrc` file like
```txt
machine gitlab.gt.vng.vn
login your-token-name
password your-token-value
```

2. Copy .netrc file to your home directory
```bash
cp .netrc ~/
```

3. Add pybase library to your project
```bash
pip install --extra-index-url https://gitlab.gt.vng.vn/api/v4/projects/2968/packages/pypi/simple/ pybase-library
```
or add into `requirements.txt`
```txt
--extra-index-url https://gitlab.gt.vng.vn/api/v4/projects/2968/packages/pypi/simple/
pybase-library==0.1.0
```

4. Import pybase library to your project
```python
from pybase_library import *
```
