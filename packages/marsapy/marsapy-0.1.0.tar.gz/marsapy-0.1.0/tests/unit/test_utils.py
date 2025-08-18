from marsa.utils import clean_input

# ---------- Regular Tests ----------

def test_clean_input_basic_text():
    # Arrange
    text = "This is a normal sentence."
    expected = "this is a normal sentence."
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_with_urls():
    # Arrange
    text = "Check out this link: https://example.com and also www.test.com"
    expected = "check out this link:  and also"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_with_email():
    # Arrange
    text = "Contact me at user@example.com for more info"
    expected = "contact me at  for more info"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_with_emojis():
    # Arrange
    text = "I love this! 😀🎉"
    expected = "i love this! :grinning_face::party_popper:"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_mixed_content():
    # Arrange
    text = "Great product! 👍 Visit https://shop.com or email help@shop.com"
    expected = "great product! :thumbs_up: visit  or email"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_uppercase_conversion():
    # Arrange
    text = "THIS IS ALL CAPS TEXT"
    expected = "this is all caps text"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_whitespace_strip():
    # Arrange
    text = "   Text with extra spaces   "
    expected = "text with extra spaces"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

# ---------- Edge Case Tests ----------

def test_clean_input_empty_string():
    # Arrange
    text = ""
    expected = ""
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_only_whitespace():
    # Arrange
    text = "   \n\t   "
    expected = ""
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_only_urls():
    # Arrange
    text = "https://example.com www.test.com"
    expected = ""
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_only_email():
    # Arrange
    text = "user@example.com"
    expected = ""
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected

def test_clean_input_complex_urls():
    # Arrange
    text = "Visit https://example.com/path?param=value or http://test.org"
    expected = "visit  or"
    
    # Act
    result = clean_input(text)
    
    # Assert
    assert result == expected