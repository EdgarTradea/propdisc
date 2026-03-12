import json
import os

STATE_FILE = "state.json"

def load_state():
    """Load the state from the JSON file. Initialize if it doesn't exist."""
    if not os.path.exists(STATE_FILE):
        return {
            "GoatFunded": None,
            "FTMO": None,
            "neomaaafunds": None
        }
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save the state to the JSON file."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def update_handle_state(handle, latest_tweet_id):
    """Update the latest seen tweet ID for a specific handle."""
    state = load_state()
    state[handle] = latest_tweet_id
    save_state(state)
