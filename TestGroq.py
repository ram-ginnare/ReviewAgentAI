import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv is not installed.")
    print("Run: pip install python-dotenv")
    sys.exit(1)

try:
    from groq import Groq
except ImportError:
    print("ERROR: Groq SDK is not installed.")
    print("Run: pip install groq")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

print("=" * 60)
print("reviewagentai - Groq API Test")
print("=" * 60)
print(f"Project folder : {ROOT}")
print(f".env found     : {(ROOT / '.env').exists()}")
print(f"API key found  : {'YES' if api_key else 'NO'}")
print(f"API key format : {'looks valid' if api_key and len(api_key) > 20 else 'missing/too short'}")
print(f"Model          : {model}")
print()

if not api_key:
    print("RESULT: FAILED - GROQ_API_KEY was not loaded from .env")
    print("Check that .env is in the same folder as TestGroq.py and contains:")
    print("GROQ_API_KEY=your-real-key")
    sys.exit(2)

try:
    client = Groq(api_key=api_key)
    print("Groq client    : CREATED")
    print("Sending test request...")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: GROQ_TEST_OK",
            }
        ],
        temperature=0,
        max_tokens=20,
    )

    content = (response.choices[0].message.content or "").strip()
    print()
    print("RESULT: SUCCESS - Groq API request completed")
    print(f"Model response: {content}")

    if content:
        print("API key/authentication: WORKING")
        print("Model access: WORKING")
    else:
        print("WARNING: Groq responded but returned empty content.")

except Exception as exc:
    error_type = type(exc).__name__
    message = str(exc)
    print()
    print("RESULT: FAILED - Groq API request failed")
    print(f"Error type : {error_type}")
    print(f"Error      : {message}")
    print()

    lowered = message.lower()
    if "401" in lowered or "authentication" in lowered or "invalid api key" in lowered or "unauthorized" in lowered:
        print("Diagnosis: API key authentication failed.")
        print("Check GROQ_API_KEY in .env.")
    elif "403" in lowered or "permission" in lowered or "forbidden" in lowered:
        print("Diagnosis: API key is recognized but access is forbidden.")
    elif "429" in lowered or "rate limit" in lowered or "quota" in lowered or "insufficient_quota" in lowered:
        print("Diagnosis: Groq quota/rate-limit issue.")
        print("Your API key may be valid, but the account/model request is currently rate limited or out of quota.")
    elif "model" in lowered and ("not found" in lowered or "invalid" in lowered or "does not exist" in lowered):
        print("Diagnosis: The configured GROQ_MODEL is unavailable or invalid.")
        print(f"Current model: {model}")
    elif "connection" in lowered or "timeout" in lowered or "network" in lowered or "dns" in lowered:
        print("Diagnosis: Network/connectivity problem while reaching Groq.")
    else:
        print("Diagnosis: Groq SDK/API returned an unexpected error.")

    print("Your API key was NOT printed by this script.")
    sys.exit(3)
