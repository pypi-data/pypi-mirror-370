# tests/test_core.py
from decimal import Decimal, ROUND_HALF_UP
import pytest

from always_decimal import ensure_decimal, DecimalCoercionError, to_decimal_exact


def test_decimal_passthrough():
    assert ensure_decimal(Decimal("1.2300")) == Decimal("1.2300")


def test_from_int():
    assert ensure_decimal(7) == Decimal(7)


def test_from_float_no_scale():
    d = ensure_decimal(0.1)  # exact binary float -> long Decimal
    assert isinstance(d, Decimal)


def test_from_float_with_scale():
    assert ensure_decimal(0.1, scale=2) == Decimal("0.10")


def test_from_string():
    assert ensure_decimal("1.2345", scale=3, rounding=ROUND_HALF_UP) == Decimal("1.235")


def test_invalid_string_raises():
    with pytest.raises(DecimalCoercionError):
        ensure_decimal("not a number")


def test_normalize():
    assert str(ensure_decimal("1.2300", scale=4, normalize=True)) == "1.23"


# --- NEW exact-conversion tests ---


def test_to_decimal_exact_from_float_matches_from_float_builtin():
    # Should be identical to Decimal.from_float for exactness
    x = 0.1
    assert to_decimal_exact(x) == Decimal.from_float(x)


def test_to_decimal_exact_roundtrip_float_equality():
    # Converting back to float yields the original float bit pattern value
    x = 0.1
    d = to_decimal_exact(x)
    assert float(d) == x


def test_to_decimal_exact_negative_zero_sign():
    # Preserve -0.0 sign
    x = -0.0
    d = to_decimal_exact(x)
    assert d == Decimal.from_float(-0.0)
    # Robust sign/zero checks across Python versions/contexts
    assert d.is_zero()
    assert d.is_signed()
    # Optional: allow either string form
    assert str(d) in ("-0", "-0.0")


def test_to_decimal_exact_decimal_passthrough():
    d = Decimal("1.2300")
    assert to_decimal_exact(d) is d or to_decimal_exact(d) == d  # accept same object or equal


def test_to_decimal_exact_rejects_unsupported():
    with pytest.raises(TypeError):
        to_decimal_exact("1.23")  # only float or Decimal allowed
