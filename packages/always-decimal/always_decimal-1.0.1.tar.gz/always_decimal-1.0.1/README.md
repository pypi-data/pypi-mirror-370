
# always-decimal

A tiny Python package to safely convert floats, strings, and numbers into [`Decimal`](https://docs.python.org/3/library/decimal.html) objects.  
It solves common headaches when comparing **PostgreSQL `numeric`** values with Python floats by ensuring **consistent `Decimal` values**.

---

## ✨ Features

- 🔒 **Exact conversion** from `float` → `Decimal` (no hidden rounding).
- ⚖️ **Configurable coercion**: set scale, rounding mode, normalize trailing zeros.
- 🧩 Works with `float`, `int`, `str`, or `Decimal`.
- 🛡️ Raises clear `DecimalCoercionError` on invalid inputs.
- 🐍 Compatible with Python **3.10+**.
- 📦 Easy install via **uv** or **pip**.

---

## 📦 Installation

### Using [uv](https://github.com/astral-sh/uv) (recommended)

```bash
uv add always-decimal
````

### Using pip

```bash
pip install always-decimal
```

For local development:

```bash
uv pip install -e ".[dev]"
# or
pip install -e ".[dev]"
```

---

## 🚀 Usage

```python
from always_decimal import ensure_decimal, to_decimal_exact

# 1. Exact conversion: no rounding, no scale changes
d1 = to_decimal_exact(0.1)
print(d1)
# Decimal('0.1000000000000000055511151231257827021181583404541015625')

# 2. Safe coercion with fixed scale
price = ensure_decimal(19.995, scale=2)
print(price)
# Decimal('20.00')  (ROUND_HALF_EVEN default)

# 3. String input with quantization
val = ensure_decimal("1.2345", scale=3)
print(val)
# Decimal('1.235')

# 4. Normalizing (remove trailing zeros)
norm = ensure_decimal("1.2300", scale=4, normalize=True)
print(norm)
# Decimal('1.23')
```

---

## ⚙️ API

### `to_decimal_exact(value: float | Decimal) -> Decimal`

Convert a `float` or `Decimal` to a `Decimal` **exactly**:

* `float` → `Decimal.from_float(value)`
* `Decimal` → returned as-is
  Raises `TypeError` for other types.

### `ensure_decimal(value, *, scale=None, rounding=ROUND_HALF_EVEN, clamp_exp=True, normalize=False) -> Decimal`

Convert and coerce input to `Decimal`.

* **scale**: number of fractional digits to quantize (e.g., 2 → cents).
* **rounding**: rounding mode (default: bankers rounding).
* **clamp\_exp**: clamp exponents to context limits.
* **normalize**: trim trailing zeros.

---

## 🧪 Running Tests

```bash
make test
```

or directly:

```bash
pytest
```

---

## 📄 License

[MIT](LICENSE)

---

## 🙌 Contributing

Issues and PRs are welcome!
Please format with `ruff`, type-check with `mypy`, and run `pytest` before submitting.
