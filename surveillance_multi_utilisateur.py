import os
from recuperer_emails import list_emails_for_user

def lister_tokens_utilisateurs():
    """Retourne la liste des fichiers de jetons Gmail enregistrés"""
    return [f for f in os.listdir('.') if f.startswith('token_') and f.endswith('.pickle')]

def lancer_surveillance_pour_tous():
    """Récupère les e-mails pour chaque utilisateur connecté"""
    tokens = lister_tokens_utilisateurs()

    if not tokens:
        print("❌ Aucun utilisateur connecté. Lance d'abord oauth_user.py")
        return

    for token_file in tokens:
        print(f"\n🔍 Traitement de : {token_file}")
        try:
            list_emails_for_user(token_file)
        except Exception as e:
            print(f"⚠️ Erreur pour {token_file} : {e}")

if __name__ == "__main__":
    lancer_surveillance_pour_tous()
