"""Parse money and quantities into integers.

SQLite has no decimal type. Amounts are integer pence (GBP). The parser
rejects currency symbols, thousands separators, and more than two decimal
places instead of rounding them away.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def to_pence(value: object) -> int | None:
    """Return half-up pence, or None when the text is not a 2-dp GBP amount."""
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"nan", "none", "nat"}:
        return None
    if any(mark in text for mark in "£$€,"):
        return None
    try:
        amount = Decimal(text)
    except InvalidOperation:
        return None
    exponent = amount.as_tuple().exponent
    if isinstance(exponent, int) and exponent < -2:
        return None
    pennies = (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(pennies)


def to_int(value: object) -> int | None:
    """Return a whole-number quantity. Decimal quantities are rejected."""
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"nan", "none", "nat"}:
        return None
    if text[0] == "+":
        text = text[1:]
    if not text or text in {"-", "+"}:
        return None
    if text[0] == "-":
        digits = text[1:]
    else:
        digits = text
    if not digits.isdigit():
        return None
    return int(text)


def format_pence(pence: int) -> str:
    """Format integer pence as signed GBP with a thousands separator."""
    sign = "-" if pence < 0 else ""
    absolute = abs(int(pence))
    return f"{sign}£{absolute // 100:,}.{absolute % 100:02d}"
