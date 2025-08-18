import subprocess
import sys
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read API key from .env or system env
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found. Please set it in your .env file.")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def suggest_fix(cmd, error):
    prompt = f"""
    The user ran this command and got an error:
    Command: {cmd}
    Error: {error}

    Suggest ONLY the corrected command in plain text, no explanation.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def run_with_ai_fix(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        suggestion = suggest_fix(cmd, str(e))
        print(f"\nGemini Suggests: {suggestion}")
        if input("Run it? (y/n): ").lower() == "y":
            subprocess.run(suggestion, shell=True)
    except FileNotFoundError as e:
        # Handle typos like `gti`
        suggestion = suggest_fix(cmd, str(e))
        print(f"\nGemini Suggests: {suggestion}")
        if input("Run it? (y/n): ").lower() == "y":
            subprocess.run(suggestion, shell=True)

if __name__ == "__main__":
    last_cmd = " ".join(sys.argv[1:])
    run_with_ai_fix(last_cmd)
