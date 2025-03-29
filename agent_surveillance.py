import schedule
import time
import os
import pickle
from recuperer_emails import analyser_et_enregistrer_emails

# Le nom de l'utilisateur Gmail 
USER_EMAIL = None

# Essayons de trouver un token actif automatiquement
try:
    token_folder = "tokens"
    for filename in os.listdir(token_folder):
        if filename.endswith(".pickle"):
            USER_EMAIL = filename.replace("token_", "").replace(".pickle", "")
            print(f"✅ Utilisateur pour surveillance automatique : {USER_EMAIL}")
            break
except Exception as e:
    print(f"❌ Erreur lors de la détection de l'utilisateur Gmail : {e}")

def verifier_boite_mail():
    if USER_EMAIL:
        print("\n🔄 Vérification automatique de la boîte mail en cours...")
        analyser_et_enregistrer_emails(USER_EMAIL)
    else:
        print("❌ Aucun utilisateur Gmail connecté pour surveillance.")

# Planifie une vérification toutes les 2 minutes
schedule.every(2).minutes.do(verifier_boite_mail)

print("\n🤖 Agent IA Email lancé. Surveillance en cours toutes les 2 minutes.")

while True:
    schedule.run_pending()
    time.sleep(1)