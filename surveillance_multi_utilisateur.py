import os
import subprocess
from recuperer_emails import analyser_et_enregistrer_emails

def lister_tokens_utilisateurs():
    """Retourne la liste des chemins de fichiers de jetons Gmail enregistrés dans le dossier tokens/"""
    token_dir = "tokens"
    return [os.path.join(token_dir, f) for f in os.listdir(token_dir)
            if f.startswith('token_') and f.endswith('.pickle')]

def lancer_surveillance_pour_tous():
    """Récupère les e-mails pour chaque utilisateur connecté"""
    tokens = lister_tokens_utilisateurs()

    if not tokens:
        print("❌ Aucun utilisateur connecté. Lance d'abord oauth_user.py")
        return

    for token_path in tokens:
        user_email = token_path.replace("tokens/token_", "").replace(".pickle", "")
        print(f"\n🔍 Traitement de : {user_email}")
        try:
            analyser_et_enregistrer_emails(user_email)
        except Exception as e:
            print(f"⚠️ Erreur pour {user_email} : {e}")

def lancer_surveillance():
    """Lance le script de surveillance en arrière-plan"""
    try:
        subprocess.Popen(["python3", "surveillance_multi_utilisateur.py"])
        print("✅ Surveillance multi-utilisateur démarrée.")
    except Exception as e:
        print(f"❌ Erreur lancement surveillance : {e}")

if __name__ == "__main__":
    lancer_surveillance_pour_tous()