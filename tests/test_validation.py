from validation import is_valid_email, is_valid_phone

def test_valid_email():
    assert is_valid_email("ada@x.com") is True
    
def test_invalid_email():
    assert is_valid_email("ada-at-x.com") is False
    assert is_valid_email("ada@x") is False # No TLD
    
def test_valid_phone():
    assert is_valid_phone("555-0001") is True