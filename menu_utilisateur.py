import os
from recuperer_emails import list_emails_for_user
from oauth_user import authenticate_user  # Assure-toi que ce fichier existe et fonctionne

def lister_utilisateurs():
    """Liste les fichiers token Gmail déjà enregistrés"""
    fichiers = [f for f in os.listdir('.') if f.startswith('token_') and f.endswith('.pickle')]
    utilisateurs = [f.replace("token_", "").replace(".pickle", "") for f in fichiers]
    return fichiers, utilisateurs

def menu():
    while True:
        fichiers, utilisateurs = lister_utilisateurs()

        print("\n📬 MENU AGENT AI - GMAIL")
        print("==========================")
        for i, email in enumerate(utilisateurs):
            print(f"{i+1}. 📥 Récupérer les e-mails de {email}")
        print("N. ➕ Connecter un nouvel utilisateur Gmail")
        print("Q. ❌ Quitter")

        choix = input("\n➡️ Que veux-tu faire ? ")

        if choix.lower() == "q":
            print("👋 À bientôt !")
            break
        elif choix.lower() == "n":
            print("\n🔐 Lancement de la connexion Gmail...")
            try:
                new_email = authenticate_user()
                print(f"✅ Utilisateur ajouté : {new_email}")
            except Exception as e:
                print(f"❌ Erreur : {e}")
        else:
            try:
                index = int(choix) - 1
                token_file = fichiers[index]
                print(f"\n📤 Récupération des e-mails pour : {utilisateurs[index]}")
                list_emails_for_user(token_file)
            except (ValueError, IndexError):
                print("⚠️ Choix invalide.")

if __name__ == "__main__":
    menu()
