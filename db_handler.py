import sqlite3

DATABASE_NAME = "emails.db"

def creer_base():
    """Crée la base de données des e-mails si elle n'existe pas."""
    print("🔄 Création de emails.db en cours...")
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sujet TEXT,
            expediteur TEXT,
            date TEXT,
            contenu TEXT,
            utilisateur TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base emails.db créée avec succès !")

def ajouter_email(sujet, expediteur, date, contenu, utilisateur):
    """Ajoute un e-mail à la base de données."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO emails (sujet, expediteur, date, contenu, utilisateur) VALUES (?, ?, ?, ?, ?)",
                   (sujet, expediteur, date, contenu, utilisateur))
    conn.commit()
    conn.close()
    print("✅ E-mail ajouté à la base de données")

def afficher_emails():
    """Affiche les e-mails stockés dans la base."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emails")
    emails = cursor.fetchall()
    conn.close()

    if not emails:
        print("📭 Aucun e-mail enregistré.")
    else:
        print("\n📩 **E-MAILS ENREGISTRÉS** 📩")
        for email in emails:
            print(f"📬 Sujet: {email[1]}\n📨 Expéditeur: {email[2]}\n📅 Date: {email[3]}\n📜 Contenu: {email[4][:200]}...")
            print("-" * 50)

# ✅ Run only when executing this file directly
if __name__ == "__main__":
    creer_base()
    afficher_emails()
