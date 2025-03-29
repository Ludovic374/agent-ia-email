import os
from recuperer_emails import list_emails_for_user

def lister_utilisateurs():
    """Liste les e-mails disponibles à partir des fichiers token_*.pickle"""
    fichiers = [f for f in os.listdir('.') if f.startswith('token_') and f.endswith('.pickle')]
    utilisateurs = [f.replace("token_", "").replace(".pickle", "") for f in fichiers]
    return fichiers, utilisateurs

def choisir_utilisateur():
    fichiers, utilisateurs = lister_utilisateurs()

    if not utilisateurs:
        print("❌ Aucun utilisateur connecté. Lance d'abord oauth_user.py")
        return

    print("\n👤 Utilisateurs Gmail disponibles :")
    for i, email in enumerate(utilisateurs):
        print(f"{i+1}. {email}")

    choix = input("\n➡️ Choisis un utilisateur (numéro) : ")

    try:
        index = int(choix) - 1
        token_file = fichiers[index]
        print(f"\n📬 Récupération des e-mails pour : {utilisateurs[index]}")
        list_emails_for_user(token_file)
    except (ValueError, IndexError):
        print("❌ Choix invalide. Veuillez entrer un numéro valide.")

if __name__ == "__main__":
    choisir_utilisateur()
