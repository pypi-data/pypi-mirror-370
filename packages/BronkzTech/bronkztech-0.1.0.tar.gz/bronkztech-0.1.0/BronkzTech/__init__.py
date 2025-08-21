import sys
import os
from dotenv import load_dotenv  # <--- novo

vendor_path = os.path.join(os.path.dirname(__file__), "vendor")
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("Defina a variável de ambiente GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def gerar_texto(prompt: str, modelo: str = "gemini-2.5-flash"):
    model = genai.GenerativeModel(model_name=modelo)
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else response
