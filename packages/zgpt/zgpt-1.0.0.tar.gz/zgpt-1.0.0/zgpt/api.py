
import requests
import json

# Using a more recent and capable model
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

def ask_gemini(prompt, key):
    """Sends a prompt to the Gemini API and returns the response."""
    headers = {"Content-Type": "application/json"}
    params = {"key": key}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(API_URL, headers=headers, params=params, json=data, timeout=60)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        response_json = response.json()

        # Robustly access the response text
        candidates = response_json.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates found in the API response.")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise ValueError("No parts found in the API response content.")

        return parts[0].get("text", "No text found in response.").strip()

    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"
    except (ValueError, KeyError, IndexError) as e:
        # Handle cases with unexpected JSON structure
        return f"API response format is unexpected: {e}. Full response: {response.text}"
