from app import add

def test_add():
    assert add(2, 3) == 5

def test_threshold_logic():
    # This is a unit test for your decision logic[cite: 1]
    value_high = 60
    value_low = 20
    
    # Logic check
    assert (value_high > 50) is True  # Should be maintenance
    assert (value_low > 50) is False # Should be online