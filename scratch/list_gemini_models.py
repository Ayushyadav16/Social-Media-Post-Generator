import sys
import os

if len(sys.argv) < 2:
    print("Usage: python list_gemini_models.py <YOUR_GOOGLE_API_KEY>")
    sys.exit(1)

api_key = sys.argv[1]

print("--- DIAGNOSING GOOGLE GEMINI MODELS ---")
print(f"Using API Key: {api_key[:6]}...{api_key[-6:] if len(api_key) > 12 else ''}")

# 1. Attempt using langchain-google-genai list models or genai list
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print("\n[Method 1] Listing via google-generativeai SDK:")
    models = list(genai.list_models())
    if not models:
        print("❌ No models returned. Your key might not have access to any models, or the API is disabled.")
    else:
        print(f"Success! Found {len(models)} models:")
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name} (supports generateContent)")
except Exception as e:
    print(f"❌ Method 1 failed: {str(e)}")

# 2. Attempt using new google-genai SDK
try:
    print("\n[Method 2] Listing via new google-genai SDK:")
    from google import genai as new_genai
    client = new_genai.Client(api_key=api_key)
    # List models
    models_response = client.models.list()
    print("Success! Available models:")
    for m in models_response:
        print(f" - {m.name}")
except Exception as e:
    print(f"❌ Method 2 failed: {str(e)}")
