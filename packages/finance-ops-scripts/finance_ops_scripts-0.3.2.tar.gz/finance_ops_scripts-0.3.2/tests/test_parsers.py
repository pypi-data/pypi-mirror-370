from scripts.python.ramp_export_mapper import _to_decimal_str, _to_iso_date


def test_to_iso_date_accepts_common_formats():
    assert _to_iso_date("2024-12-31") == "2024-12-31"
    assert _to_iso_date("12/31/2024") == "2024-12-31"
    assert _to_iso_date("12/31/24") == "2024-12-31"
    assert _to_iso_date("31-Dec-2024") == "2024-12-31"


def test_to_iso_date_bad_returns_blank():
    assert _to_iso_date("") == ""
    assert _to_iso_date("not-a-date") == ""


def test_to_decimal_str_normalizes():
    assert _to_decimal_str("$1,234.5") == "1234.50"
    assert _to_decimal_str("-") == "0.00"  # treated as blank → 0.00
    assert _to_decimal_str("  ") == "0.00"
    assert _to_decimal_str("10") == "10.00"


def test_to_decimal_str_bad_returns_blank():
    assert _to_decimal_str("abc") == ""
