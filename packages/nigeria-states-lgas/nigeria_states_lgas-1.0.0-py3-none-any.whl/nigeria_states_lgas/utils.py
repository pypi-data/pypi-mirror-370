import json
import os

# Path to JSON data
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'nigeria_states_and_lgas.json')

with open(DATA_PATH, 'r', encoding="utf-8") as f:
    NIGERIA_DATA = json.load(f)

def get_states():
    """Returns a list of all Nigerian states (including FCT)."""
    return list(NIGERIA_DATA.keys())

def get_lgas(state):
    """Returns a list of all LGAs in a given Nigerian state (case-insensitive)."""
    state = state.strip().lower()
    for s in NIGERIA_DATA:
        if s.lower() == state:
            return NIGERIA_DATA[s]
    return []

def get_all():
    """Returns a dictionary of all Nigerian states and their LGAs."""
    return NIGERIA_DATA

def search_lga(lga_name):
    """Search for an LGA and return a list of states (case-insensitive)."""
    lga_name = lga_name.strip().lower()
    results = []
    for state, lgas in NIGERIA_DATA.items():
        if any(lga.lower() == lga_name for lga in lgas):
            results.append(state)
    return results

