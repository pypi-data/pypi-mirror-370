from anonyspark.masking import (
    mask_email, mask_name, mask_date,
    mask_ssn, mask_itin, mask_phone
)

def test_mask_email():
    assert mask_email("john@example.com") == "***@example.com"
    assert mask_email("") is None
    assert mask_email(None) is None

def test_mask_name():
    assert mask_name("John") == "J***"
    assert mask_name("") is None
    assert mask_name(None) is None

def test_mask_date():
    assert mask_date("1991-08-14") == "***-**-14"
    assert mask_date("invalid") is None
    assert mask_date(None) is None

def test_mask_ssn():
    assert mask_ssn("123-45-6789") == "***-**-6789"
    assert mask_ssn("invalid") is None

def test_mask_itin():
    assert mask_itin("912-73-1234") == "***-**-1234"
    assert mask_itin("123-45-6789") is None

def test_mask_phone():
    assert mask_phone("123-456-7890") == "***-***-7890"
    assert mask_phone("(123) 456-7890") == "***-***-7890"
    assert mask_phone("invalid") is None
