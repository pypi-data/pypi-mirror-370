from digitalguide.pattern import KOMMAZAHL_PATTERN
import pytest
import re

@pytest.mark.parametrize("kommazahl", [
    "5,3",
    "5"
    "12356,23432"
])
def test_kommazahl_pattern_positiv(kommazahl):
    filter = re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)
    assert(filter.search(kommazahl))

@pytest.mark.parametrize("kommazahl", [
    "7 - 12",
    "8 und 9"
])
def test_kommazahl_pattern_multiple_positiv(kommazahl):
    filter = re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)
    assert(filter.search(kommazahl))

@pytest.mark.parametrize("kommazahl", [
    "Es sind 9 Wochen.",
    "Ich schätze 7,3 Tage"
])
def test_kommazahl_pattern_in_text_positiv(kommazahl):
    filter = re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)
    assert(filter.search(kommazahl))

@pytest.mark.parametrize("kommazahl", [
    "a",
    "b"
])
def test_kommazahl_pattern_negativ(kommazahl):
    filter = re.compile(KOMMAZAHL_PATTERN,re.IGNORECASE)
    assert(not filter.search(kommazahl))