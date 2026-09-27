import csv
import os
from database import get_or_create_person, insert_achievement

STAGING_DIR = "data_staging"

def import_csv_adapter(filename, source_name, comp_name):
    filepath = os.path.join(STAGING_DIR, filename)
    if not os.path.exists(filepath):
        return {"status": "error", "message": f"Datei {filepath} nicht gefunden."}
    
    count = 0
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row.get("Name", "").strip()
            if not name:
                continue
                
            country = row.get("Country", "").strip()
            year = row.get("Year", "").strip()
            medal = row.get("Medal", "").strip()

            person_id = get_or_create_person(name, country)

            insert_achievement(
                person_id=person_id,
                source_db=source_name,
                competition=comp_name,
                medal=medal,
                year=int(year) if year.isdigit() else None
            )
            count += 1
            
    return {"status": "success", "message": f"{count} Datensätze aus {filename} importiert."}