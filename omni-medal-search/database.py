import sqlite3
import os
from thefuzz import process

DB_PATH = "competitions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            canonical_name TEXT UNIQUE,
            country TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            source_db TEXT,
            competition TEXT,
            medal TEXT,
            year INTEGER,
            FOREIGN KEY(person_id) REFERENCES persons(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_person(name, country=None):
    """
    Entity Resolution: Sucht nach ähnlichen Namen, um Duplikate zu vermeiden.
    Ab 85% Ähnlichkeit gehen wir von der gleichen Person aus.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, canonical_name FROM persons")
    all_persons = cursor.fetchall()
    
    if all_persons:
        choices = {row[0]: row[1] for row in all_persons}
        best_match = process.extractOne(name, choices)
        
        if best_match and best_match[1] >= 85:
            conn.close()
            return best_match[2] 
        
    cursor.execute("INSERT INTO persons (canonical_name, country) VALUES (?, ?)", (name, country))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return new_id

def insert_achievement(person_id, source_db, competition, medal, year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM achievements 
        WHERE person_id = ? AND competition = ? AND medal = ? AND year = ?
    ''', (person_id, competition, medal, year))
    
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO achievements (person_id, source_db, competition, medal, year)
            VALUES (?, ?, ?, ?, ?)
        ''', (person_id, source_db, competition, medal, year))
        conn.commit()
    conn.close()