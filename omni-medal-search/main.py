from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import sqlite3
import database
import importers

app = FastAPI()

database.init_db()

class FilterCriteria(BaseModel):
    competition: str
    medal: str

class SearchRequest(BaseModel):
    filters: List[FilterCriteria]

@app.post("/api/import/{competition}")
def run_import(competition: str):
    """
    Triggert den Import für eine spezifische Datenbank.
    Erwartet z.B. eine imo_data.csv im Ordner data_staging.
    """
    filename = f"{competition.lower()}_data.csv"
    result = importers.import_csv_adapter(filename, f"{competition.upper()}_Web", competition.upper())
    return result

@app.post("/api/search")
def search_persons(request: SearchRequest):
    """
    Sucht Personen, die ALLE übergebenen Kriterien erfüllen (Schnittmenge).
    """
    if not request.filters:
        return []

    conn = sqlite3.connect(database.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    conditions = []
    params = []
    
    for f in request.filters:
        conditions.append("(a.competition = ? AND a.medal = ?)")
        params.extend([f.competition, f.medal])

    where_clause = " OR ".join(conditions)
    num_conditions = len(request.filters)

    query = f'''
        SELECT p.id, p.canonical_name, p.country, 
               GROUP_CONCAT(a.competition || ' ' || a.medal || ' (' || ifnull(a.year, 'N/A') || ')', ' | ') as all_achievements
        FROM persons p
        JOIN achievements a ON p.id = a.person_id
        WHERE {where_clause}
        GROUP BY p.id
        HAVING COUNT(DISTINCT a.competition || a.medal) = ?
    '''
    params.append(num_conditions)
    
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

app.mount("/", StaticFiles(directory="static", html=True), name="static")