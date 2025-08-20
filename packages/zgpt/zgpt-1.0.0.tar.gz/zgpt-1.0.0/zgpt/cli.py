
import argparse
import sys
from zgpt.api import ask_gemini
from zgpt.config import load_key, save_key, delete_key

def main():
    """Main function to handle command-line arguments and execution."""
    parser = argparse.ArgumentParser(
        prog="zgpt",
        description="A versatile CLI assistant powered by the Gemini API."
    )
    parser.add_argument("prompt", nargs="*", help="The prompt to send to the AI model.")
    parser.add_argument("--init", action="store_true", help="Initialize and save your Gemini API key.")
    parser.add_argument("--revoke", action="store_true", help="Remove the saved API key.")
    args = parser.parse_args()

    if args.init:
        key = input("🔑 Enter your Gemini API key: ").strip()
        if not key:
            print("❌ API key cannot be empty.")
            sys.exit(1)
        save_key(key)
        print("✅ API key has been saved successfully!")
        return

    if args.revoke:
        delete_key()
        print("🗑️ API key has been removed.")
        return

    api_key = load_key()
    if not api_key:
        print("⚠️ API key not found. Please run 'zgpt --init' to set it up.")
        sys.exit(1)

    query = " ".join(args.prompt)
    if not query.strip():
        print("💡 How to use: zgpt \"your question goes here\"")
        print("   Example: zgpt \"what is the capital of France?\"")
        return

    print("🤔 Thinking...")
    try:
        response = ask_gemini(query, api_key)
        print(f"🤖\n\n{response}")
    except Exception as e:
        print(f"🔥 An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
