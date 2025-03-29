import os
import shutil
from datetime import datetime

DB_FILE = "emails.db"
BACKUP_DIR = "backups"

os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    if os.path.exists(DB_FILE):
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"emails_backup_{date_str}.db")
        shutil.copy2(DB_FILE, backup_file)
        print(f"✅ Sauvegarde effectuée : {backup_file}")
    else:
        print("❌ Base de données non trouvée.")

if __name__ == "__main__":
    backup_database()