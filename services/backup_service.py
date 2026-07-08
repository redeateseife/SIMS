# services/backup_service.py

from datetime import datetime
from config import BACKUP_DIR, CSV_FILE
from services.inventory_service import Inventory

def save_and_backup(inventory: Inventory) -> str:
    
    inventory.df.to_csv(CSV_FILE, index=False)

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"inventory_{timestamp}.csv"
    backup_path.write_bytes(CSV_FILE.read_bytes())

    return backup_path.name
