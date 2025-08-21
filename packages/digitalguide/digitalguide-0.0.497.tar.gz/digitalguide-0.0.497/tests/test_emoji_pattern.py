from digitalguide.pattern import EMOJI_PATTERN
import pytest
import re

@pytest.mark.parametrize("emoji", [
    "🏗️",
    "📚"
])
def test_emoji_pattern_positive(emoji):
    filter = re.compile(EMOJI_PATTERN,re.IGNORECASE)
    assert(filter.search(emoji))

@pytest.mark.parametrize("emoji", [
    "🏗️📚",
    "📚📚"
])
def test_emoji_pattern_multiple_positive(emoji):
    filter = re.compile(EMOJI_PATTERN,re.IGNORECASE)
    assert(filter.search(emoji))

@pytest.mark.parametrize("emoji", [
    "text🏗️text📚text",
    "text📚text📚text"
])
def test_emoji_pattern_in_text_negative(emoji):
    filter = re.compile(EMOJI_PATTERN,re.IGNORECASE)
    assert(filter.search(emoji))

@pytest.mark.parametrize("emoji", [
    "a",
    "b"
])
def test_emoji_pattern_negative(emoji):
    filter = re.compile(EMOJI_PATTERN,re.IGNORECASE)
    assert(not filter.search(emoji))