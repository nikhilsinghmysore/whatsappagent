"""Tests for agent prompts and emergency detection."""

from src.agent.prompts import EMERGENCY_KEYWORDS
from src.agent.claude import check_emergency_keywords


def test_emergency_chest_pain():
    """Test detection of chest pain."""
    result = check_emergency_keywords("I have severe chest pain")
    assert result == "chest_pain"


def test_emergency_breathing():
    """Test detection of breathing difficulty."""
    result = check_emergency_keywords("I'm having breathing difficulty")
    assert result == "breathing"


def test_emergency_unconscious():
    """Test detection of unconsciousness."""
    result = check_emergency_keywords("He is unconscious")
    assert result == "unconscious"


def test_emergency_bleeding():
    """Test detection of severe bleeding."""
    result = check_emergency_keywords("There is heavy bleeding from the wound")
    assert result == "severe_bleeding"


def test_emergency_stroke():
    """Test detection of stroke signs."""
    result = check_emergency_keywords("She has stroke signs")
    assert result == "stroke"


def test_emergency_suicidal():
    """Test detection of suicidal ideation."""
    result = check_emergency_keywords("I want to end my life")
    assert result == "suicidal"


def test_no_emergency():
    """Test that normal messages don't trigger emergency."""
    result = check_emergency_keywords("I have a fever and want to book a doctor")
    assert result is None


def test_case_insensitive():
    """Test case insensitivity of emergency detection."""
    result = check_emergency_keywords("CHEST PAIN IS KILLING ME")
    assert result == "chest_pain"
