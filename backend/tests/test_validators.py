from app.utils.validators import validate_file_extension, validate_file_size, is_valid_email, is_valid_phone

def test_valid_pdf_extension():
    assert validate_file_extension("resume.pdf") == True
    assert validate_file_extension("RESUME.PDF") == True

def test_invalid_extension():
    assert validate_file_extension("resume.docx") == False
    assert validate_file_extension("resume.txt") == False

def test_valid_file_size():
    assert validate_file_size(5 * 1024 * 1024, 10) == True  # 5MB < 10MB
    assert validate_file_size(10 * 1024 * 1024, 10) == True # 10MB = 10MB

def test_oversized_file():
    assert validate_file_size(11 * 1024 * 1024, 10) == False # 11MB > 10MB

def test_valid_email():
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("user.name+tag@domain.co.uk") == True

def test_invalid_email():
    assert is_valid_email("invalid-email") == False
    assert is_valid_email("test@") == False
    assert is_valid_email("@example.com") == False

def test_valid_phone():
    assert is_valid_phone("+1234567890") == True
    assert is_valid_phone("123-456-7890") == True

def test_invalid_phone():
    assert is_valid_phone("abc") == False
