from dotenv import load_dotenv
load_dotenv()
import requests
import os

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

def interroger_mistral(question, contexte):
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-small",
        "messages": [
            {"role": "system", "content": "Tu es un assistant pour analyser des e-mails importants."},
            {"role": "user", "content": f"Voici les e-mails:\n{contexte}\n\nQuestion : {question}"}
        ]
    }

    response = requests.post(MISTRAL_URL, json=payload, headers=headers)

    try:
        data = response.json()
    except Exception as e:
        return f"Erreur de parsing JSON : {e} | contenu brut : {response.text}"

    if "choices" in data and data["choices"]:
        return data["choices"][0]["message"]["content"]
    else:
        return f"Réponse inattendue de Mistral : {data}"