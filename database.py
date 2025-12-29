import sqlite3
from datetime import datetime
import json
import os

class Database:
    def __init__(self, db_path='data/applications.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                job_url TEXT,
                date_applied TIMESTAMP,
                status TEXT DEFAULT 'pending',
                resume_used TEXT,
                cover_letter TEXT,
                notes TEXT,
                response TEXT,
                salary_range TEXT,
                location TEXT,
                job_type TEXT
            )
        ''')
        
        # Create templates table for saving resume/cover letter templates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_date TIMESTAMP,
                last_used TIMESTAMP
            )
        ''')
        
        # Create follow_ups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follow_ups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                follow_up_date TIMESTAMP,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully!")
    
    def add_application(self, company, position, job_url=None, 
                       resume=None, cover_letter=None, notes=None,
                       salary_range=None, location=None, job_type=None):
        """Log a new application"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO applications 
            (company, position, job_url, date_applied, resume_used, 
             cover_letter, notes, salary_range, location, job_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company, position, job_url, datetime.now(), 
              resume, cover_letter, notes, salary_range, location, job_type))
        
        conn.commit()
        app_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ Application logged! ID: {app_id}")
        return app_id
    
    def get_applications(self, limit=10):
        """Get recent applications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM applications 
            ORDER BY date_applied DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        applications = []
        for row in cursor.fetchall():
            applications.append(dict(zip(columns, row)))
        
        conn.close()
        return applications
    
    def update_status(self, app_id, status):
        """Update application status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        valid_statuses = ['pending', 'applied', 'interview', 'rejected', 'offer', 'accepted']
        if status not in valid_statuses:
            print(f"⚠️ Invalid status. Use one of: {valid_statuses}")
            return
        
        cursor.execute('''
            UPDATE applications 
            SET status = ?, response = ?
            WHERE id = ?
        ''', (status, datetime.now(), app_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Updated application {app_id} to {status}")
    
    def get_stats(self):
        """Get application statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM applications")
        total = cursor.fetchone()[0]
        
        # Applications by status
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM applications 
            GROUP BY status
        """)
        by_status = cursor.fetchall()
        
        # Applications this week
        cursor.execute("""
            SELECT COUNT(*) 
            FROM applications 
            WHERE date_applied > datetime('now', '-7 days')
        """)
        this_week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'by_status': by_status,
            'this_week': this_week
        }
    
    def save_template(self, name, template_type, content):
        """Save a resume or cover letter template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (name, type, content, created_date)
            VALUES (?, ?, ?, ?)
        ''', (name, template_type, content, datetime.now()))
        
        conn.commit()
        conn.close()
        print(f"✅ Template '{name}' saved!")
    
    def get_templates(self, template_type=None):
        """Get saved templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if template_type:
            cursor.execute('''
                SELECT * FROM templates 
                WHERE type = ?
                ORDER BY created_date DESC
            ''', (template_type,))
        else:
            cursor.execute('''
                SELECT * FROM templates 
                ORDER BY created_date DESC
            ''')
        
        templates = cursor.fetchall()
        conn.close()
        return templates
    # Add this to your existing database.py file (add these methods to the Database class)

    def create_resume_table(self):
        """Create resumes table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                filename TEXT,
                content TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0,
                created_date TIMESTAMP,
                last_used TIMESTAMP,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_resume(self, name, content, filename=None, description=None):
        """Add a new resume"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO resumes (name, filename, content, description, created_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, filename, content, description, datetime.now()))
        
        conn.commit()
        resume_id = cursor.lastrowid
        conn.close()
        
        return resume_id

    def get_all_resumes(self):
        """Get all saved resumes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, filename, description, created_date, is_default
            FROM resumes
            ORDER BY created_date DESC
        ''')
        
        columns = ['id', 'name', 'filename', 'description', 'created_date', 'is_default']
        resumes = []
        for row in cursor.fetchall():
            resumes.append(dict(zip(columns, row)))
        
        conn.close()
        return resumes

    def get_resume_by_id(self, resume_id):
        """Get a specific resume"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        resume = cursor.fetchone()
        conn.close()
        
        return resume

    def set_default_resume(self, resume_id):
        """Set a resume as default"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, unset all defaults
        cursor.execute('UPDATE resumes SET is_default = 0')
        
        # Set the selected one as default
        cursor.execute('UPDATE resumes SET is_default = 1 WHERE id = ?', (resume_id,))
        
        conn.commit()
        conn.close()