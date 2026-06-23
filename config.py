from pathlib import Path

DATA_DIR = Path("data")
BACKUP_DIR = DATA_DIR / "backups"
CSV_FILE = DATA_DIR / "inventory.csv"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)