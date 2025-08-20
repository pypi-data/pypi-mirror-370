
import os
import json

# Define a secure and standard path for configuration
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "zgpt")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

def save_key(key):
    """Saves the API key to the config file."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump({"api_key": key}, f, indent=4)
    except IOError as e:
        print(f"Error saving key: {e}")

def load_key():
    """Loads the API key from the config file."""
    if not os.path.exists(CONFIG_PATH):
        return None
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            return config.get("api_key")
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error loading key: {e}")
        return None

def delete_key():
    """Deletes the config file containing the API key."""
    if os.path.exists(CONFIG_PATH):
        try:
            os.remove(CONFIG_PATH)
        except OSError as e:
            print(f"Error removing key file: {e}")
