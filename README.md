# flitenv

Manage venvs for flit project.

## Installation

```bash
python3 -m pip install flitenv
```

## Usage

Install deps from `lint` extras into `.venvs/lint`:

```bash
flitenv lint install
```

Run `.venvs/lint/bin/flake8`:

```bash
flitenv lint run flake8
```
