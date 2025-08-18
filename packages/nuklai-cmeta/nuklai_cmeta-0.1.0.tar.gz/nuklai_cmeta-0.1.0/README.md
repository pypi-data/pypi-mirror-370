# Nuklai Nexus Compact Metadata Standard (CMeta)

[![CI](https://github.com/Nuklai/cmeta/actions/workflows/ci.yml/badge.svg)](https://github.com/Nuklai/cmeta/actions/workflows/ci.yml)

**CMeta** is a compact metadata format for describing data lakes, tables, and columns in a way that is:

- 🪶 **Token-efficient**: compresses schema/metadata for LLMs with narrow context windows
- 🧑‍💻 **Human-readable**: easy to read and edit manually
- 🔄 **Reversible**: can be converted to and from JSON (compact or verbose)

This package provides Python utilities to:

- Parse **CMeta text ⇄ JSON**
- Convert to/from a **compact JSON** structure
- Convert to/from a **flat, extended JSON** structure (very verbose for some specific Nexus use cases)

---

## ✨ Installation

```bash
uv add nuklai-cmeta
````

> Uses [uv](https://github.com/astral-sh/uv). You can also install with `pip install nuklai-cmeta` if you prefer.

---

## 📐 CMeta v1 Format

* **Hierarchy**:

  * Lake → Tables → Columns
  * `:` denotes containers
  * `*` denotes columns

* **Descriptions**: in `[ ... ]`

* **Types**: in `< ... >` using full SQL types (`string`, `int`, `boolean`, `date`, `timestamp`, etc.)

* **Nested fields**: use dot notation (`car.engine.horsepower`)

* **Escape rules**:

  * `]` → `\]`
  * `<` → `\<`
  * `>` → `\>`

**Example:**

```
Webshop[Contains all webshop data]:
  users[Contains all registered users]:
    * user_id<int>[Unique ID of a user]
    * name<string>[Full name of a user]
    * email<string>[Email address]
  orders[Customer orders]:
    * id<int>[Order id]
    * total<double>[Total amount]
    * created_at<timestamp>[When created]
```

---

## 🔧 Usage

### Parse CMeta text → Model

```python
from cmeta import parse_cmeta

text = """
Webshop[Contains all webshop data]:
  users[Contains all registered users]:
    * user_id<int>[Unique ID]
    * name<string>[Full name]
"""

model = parse_cmeta(text)
print(model.lakes[0].tables[0].columns[0].name)
# "user_id"
```

---

### Model → CMeta text

```python
from cmeta import to_cmeta

cmeta_str = to_cmeta(model)
print(cmeta_str)
```

---

### Compact JSON

```python
from cmeta import model_to_compact_json, compact_json_to_model

cj = model_to_compact_json(model)
print(cj[0]["tables"][0]["columns"][0])
# {'name': 'user_id', 'type': 'int', 'description': 'Unique ID'}

m2 = compact_json_to_model(cj)
assert to_cmeta(m2) == to_cmeta(model)
```

**Compact JSON format:**

```json
[
  {
    "name": "Webshop",
    "description": "Contains all webshop data",
    "tables": [
      {
        "name": "users",
        "description": "Contains all registered users",
        "columns": [
          {"name": "user_id", "type": "int", "description": "Unique ID"}
        ]
      }
    ]
  }
]
```

---

### Extended JSON (flat, very verbose)

```python
from cmeta import model_to_extended_json, extended_json_to_model

ej = model_to_extended_json(model)
print(ej[0])
# {
#   'columnName': 'user_id',
#   'columnDescription': 'Unique ID',
#   'dataType': 'int',
#   'sourceDescription': 'Contains all webshop data',
#   'sourceName': 'Webshop',
#   'tableDescription': 'Contains all registered users',
#   'tableName': 'users'
# }

m3 = extended_json_to_model(ej)
```

**Extended JSON format:**

```json
[
  {
    "columnName": "user_id",
    "columnDescription": "Unique ID",
    "dataType": "int",
    "sourceDescription": "Contains all webshop data",
    "sourceName": "Webshop",
    "tableDescription": "Contains all registered users",
    "tableName": "users"
  }
]
```

---

## ✅ Supported Data Types

CMeta supports common datatypes:

* `string`
* `int`, `bigint`
* `float`, `double`, `decimal`
* `boolean`
* `date`, `timestamp`
* `json`, `array`, `map`

---

## 🧪 Development

Clone and set up:

```bash
uv venv && source .venv/bin/activate
make install
```

Run checks:

```bash
make ci     # lint + typecheck + test
make lint   # ruff
make format # autoformat
make test   # pytest
```

---

## 🚀 Publishing

Dev workflow for trusted contributors:

1. Bump the version in `pyproject.toml`.
2. Commit & push to `main`.
3. Tag the release:

   ```bash
   git tag v0.1.0 && git push origin v0.1.0
   ```
4. The GitHub Actions workflow will:

   * run tests
   * build wheels/sdist
   * publish to PyPI

---

## 📄 License

MIT — free for personal and commercial use.
