"""
Database Module - Αποθήκευση και διαχείριση δεδομένων
"""

import sqlite3
from datetime import datetime
from typing import List, Dict
import json


class Database:
    """Database για αποθήκευση conflict data"""
    
    def __init__(self, db_path='conflicts.db'):
        self.db_path = db_path
        self.conn = None
    
    
    def initialize(self):
        """Δημιουργία database και tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Conflicts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                lat REAL,
                lng REAL,
                region TEXT,
                threat_level TEXT,
                status TEXT,
                type TEXT,
                casualties INTEGER,
                displaced INTEGER,
                source TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conflict history table (για timeline)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conflict_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conflict_name TEXT NOT NULL,
                event_type TEXT,
                description TEXT,
                casualties INTEGER,
                event_date TIMESTAMP,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_location TEXT NOT NULL,
                to_location TEXT NOT NULL,
                connection_type TEXT,
                description TEXT,
                strength REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_conflicts INTEGER,
                total_casualties INTEGER,
                total_displaced INTEGER,
                critical_count INTEGER,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✓ Database initialized")
    
    
    def save_conflicts(self, conflicts: List[Dict]):
        """Αποθήκευση conflicts"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        
        for conflict in conflicts:
            # Check if exists
            cursor.execute('''
                SELECT id FROM conflicts WHERE location = ?
            ''', (conflict.get('location'),))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute('''
                    UPDATE conflicts SET
                        name = ?,
                        lat = ?,
                        lng = ?,
                        region = ?,
                        threat_level = ?,
                        status = ?,
                        type = ?,
                        casualties = ?,
                        displaced = ?,
                        source = ?,
                        data = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE location = ?
                ''', (
                    conflict.get('name'),
                    conflict.get('lat'),
                    conflict.get('lng'),
                    conflict.get('region'),
                    conflict.get('threat_level'),
                    conflict.get('status'),
                    conflict.get('type'),
                    conflict.get('casualties', 0),
                    conflict.get('displaced', 0),
                    conflict.get('source'),
                    json.dumps(conflict),
                    conflict.get('location')
                ))
            else:
                # Insert new
                cursor.execute('''
                    INSERT INTO conflicts (
                        name, location, lat, lng, region,
                        threat_level, status, type,
                        casualties, displaced, source, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conflict.get('name'),
                    conflict.get('location'),
                    conflict.get('lat'),
                    conflict.get('lng'),
                    conflict.get('region'),
                    conflict.get('threat_level'),
                    conflict.get('status'),
                    conflict.get('type'),
                    conflict.get('casualties', 0),
                    conflict.get('displaced', 0),
                    conflict.get('source'),
                    json.dumps(conflict)
                ))
        
        self.conn.commit()
    
    
    def get_recent_conflicts(self, limit=50) -> List[Dict]:
        """Λήψη πρόσφατων conflicts"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conflicts 
            ORDER BY updated_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conflicts = []
        
        for row in rows:
            conflict = dict(row)
            # Parse JSON data
            if conflict.get('data'):
                try:
                    conflict.update(json.loads(conflict['data']))
                except:
                    pass
            conflicts.append(conflict)
        
        return conflicts
    
    
    def get_conflict_by_id(self, conflict_id: int) -> Dict:
        """Λήψη συγκεκριμένου conflict"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM conflicts WHERE id = ?', (conflict_id,))
        
        row = cursor.fetchone()
        if row:
            conflict = dict(row)
            if conflict.get('data'):
                try:
                    conflict.update(json.loads(conflict['data']))
                except:
                    pass
            return conflict
        
        return None
    
    
    def get_conflict_timeline(self, conflict_name: str, limit=50) -> List[Dict]:
        """Λήψη timeline για συγκεκριμένο conflict"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM conflict_history 
            WHERE conflict_name = ? 
            ORDER BY event_date DESC 
            LIMIT ?
        ''', (conflict_name, limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    
    def add_conflict_event(self, conflict_name: str, event_type: str, 
                          description: str, casualties: int = 0, source: str = ''):
        """Προσθήκη event στο timeline"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conflict_history (
                conflict_name, event_type, description, 
                casualties, event_date, source
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            conflict_name,
            event_type,
            description,
            casualties,
            datetime.now(),
            source
        ))
        
        self.conn.commit()
    
    
    def save_statistics(self, stats: Dict):
        """Αποθήκευση ημερήσιων στατιστικών"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        cursor.execute('''
            INSERT OR REPLACE INTO statistics (
                date, total_conflicts, total_casualties, 
                total_displaced, critical_count, data
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            today,
            stats.get('total', 0),
            stats.get('total_casualties', 0),
            stats.get('total_displaced', 0),
            stats.get('critical', 0),
            json.dumps(stats)
        ))
        
        self.conn.commit()
    
    
    def get_statistics_history(self, days=30) -> List[Dict]:
        """Λήψη ιστορικών στατιστικών"""
        if not self.conn:
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM statistics 
            ORDER BY date DESC 
            LIMIT ?
        ''', (days,))
        
        rows = cursor.fetchall()
        stats = []
        
        for row in rows:
            stat = dict(row)
            if stat.get('data'):
                try:
                    stat.update(json.loads(stat['data']))
                except:
                    pass
            stats.append(stat)
        
        return stats
    
    
    def close(self):
        """Κλείσιμο database connection"""
        if self.conn:
            self.conn.close()
