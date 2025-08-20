# src/always_decimal/core.py
from __future__ import annotations
from decimal import Decimal, localcontext, ROUND_HALF_EVEN, InvalidOperation
from typing import Union, Optional

NumberLike = Union[float, int, str, Decimal]


class DecimalCoercionError(ValueError):
    """Raised when value cannot be coerced to Decimal."""


def _to_decimal_raw(value: NumberLike) -> Decimal:
    """
    Convert to a Decimal without changing scale. Floats are converted safely using
    Decimal.from_float to preserve the exact binary value (then you can quantize).
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int,)):
        return Decimal(value)
    if isinstance(value, (float,)):
        # captures the true binary float, e.g., 0.1 -> Decimal('0.10000000000000000555...')
        return Decimal.from_float(value)
    if isinstance(value, str):
        try:
            return Decimal(value)
        except InvalidOperation as e:
            raise DecimalCoercionError(f"Invalid decimal string: {value!r}") from e
    raise TypeError(f"Unsupported type: {type(value).__name__}")


# NEW: exact, no rounding/quantization helper
def to_decimal_exact(value: Union[float, Decimal]) -> Decimal:
    """
    Convert a float or Decimal to a Decimal with exact value and no scaling/rounding.
    - Decimal -> returned as-is (same coefficient/exponent/sign)
    - float   -> Decimal.from_float(value), preserving the exact binary float
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal.from_float(value)
    raise TypeError(f"to_decimal_exact only accepts float or Decimal, got {type(value).__name__}")


def ensure_decimal(
    value: NumberLike,
    *,
    scale: Optional[int] = None,
    rounding: str = ROUND_HALF_EVEN,
    clamp_exp: bool = True,
    normalize: bool = False,
) -> Decimal:
    """
    Coerce any supported input to Decimal. Optionally quantize to fixed `scale`
    (number of digits after the decimal point).

    Args:
      value: float|int|str|Decimal
      scale: if provided, quantize to this many fractional digits
      rounding: decimal rounding mode (default: bankers rounding)
      clamp_exp: if True, clamp very large/small exponents to context limits
      normalize: if True, remove trailing zeros (post-quantize) while preserving sign/exponent

    Returns:
      Decimal
    """
    d = _to_decimal_raw(value)

    # Use a local context so we don't mutate global Decimal context
    with localcontext() as ctx:
        ctx.rounding = rounding
        if clamp_exp:
            ctx.clamp = 1  # prevent excessively large exponents

        if scale is not None:
            # Build quantizer like: scale=2 -> Decimal('0.01'); scale=0 -> Decimal('1')
            quantizer = Decimal(1).scaleb(-scale)
            try:
                d = d.quantize(quantizer, rounding=rounding)
            except InvalidOperation as e:
                # e.g., NaN, Infinity, or context traps
                raise DecimalCoercionError(f"Cannot quantize {d!r} to scale={scale}") from e

        if normalize:
            # Normalizes exponent and trims trailing zeros; after quantize, this is usually a no-op
            d = d.normalize()

    return d
