import pytest
from nigeria_states_lgas import get_states, get_lgas, get_all, search_lga

def test_get_states():
    states = get_states()
    assert isinstance(states, list)
    assert "Lagos" in states
    assert "FCT" in states

def test_get_lgas():
    lgas = get_lgas("Kano")
    assert isinstance(lgas, list)
    assert "Nasarawa" in lgas or "Dala" in lgas  # depends on your data
    assert get_lgas("NonexistentState") == []

def test_get_all():
    all_data = get_all()
    assert isinstance(all_data, dict)
    assert "Lagos" in all_data
    assert isinstance(all_data["Lagos"], list)

def test_search_lga():
    state = search_lga("Dala")
    assert isinstance(state, list)
    assert "Kano" in state or len(state) > 0

    state_none = search_lga("NonexistentLGA")
    assert state_none == []
