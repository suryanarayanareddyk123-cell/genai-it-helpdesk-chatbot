
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: API key not found in .env")
else:
    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Say Hello! My Gemini API is working."
        )

        print("SUCCESS! Gemini API is working.")
        print(response.text)

    except Exception as e:
        print("API ERROR:")
        print(str(e))