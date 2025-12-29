import requests
from datetime import datetime
import json
import time
import os

class JobFinder:
    def __init__(self):
        self.jobs = []
        self.search_history = []
        self.load_jobs()
    
    def manual_add_job(self):
        """Let user manually add a job they found"""
        print("\n📝 ADD JOB MANUALLY")
        print("-" * 40)
        
        job = {
            'title': input("Job Title: "),
            'company': input("Company: "),
            'location': input("Location: "),
            'url': input("Job URL (press Enter to skip): "),
            'description': input("Brief Description or Requirements: "),
            'salary': input("Salary Range (press Enter to skip): "),
            'job_type': input("Job Type (remote/hybrid/onsite): "),
            'date_found': datetime.now().isoformat()
        }
        
        # Clean up empty fields
        job = {k: v for k, v in job.items() if v}
        
        self.jobs.append(job)
        self.save_jobs()
        
        print("✅ Job added successfully!")
        return job
    
    def search_github_jobs(self, keywords, location=None):
        """Search GitHub's job board (example of free API)"""
        # Note: GitHub Jobs API is deprecated, this is just an example
        # You can replace with other free job APIs like:
        # - Adzuna API (free tier)
        # - Reed API (UK jobs)
        # - USAJobs API (government jobs)
        
        print(f"🔍 Searching for '{keywords}' jobs...")
        
        # For now, return example data
        example_jobs = [
            {
                'title': f'{keywords} Developer',
                'company': 'Example Tech Co',
                'location': location or 'Remote',
                'url': 'https://example.com/job1',
                'description': f'Looking for a {keywords} developer with 2+ years experience...',
                'date_found': datetime.now().isoformat()
            }
        ]
        
        self.jobs.extend(example_jobs)
        return example_jobs
    
    def import_from_csv(self, csv_path):
        """Import jobs from a CSV file"""
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            
            imported_count = 0
            for _, row in df.iterrows():
                job = {
                    'title': row.get('title', 'Unknown'),
                    'company': row.get('company', 'Unknown'),
                    'location': row.get('location', ''),
                    'url': row.get('url', ''),
                    'description': row.get('description', ''),
                    'date_found': datetime.now().isoformat()
                }
                self.jobs.append(job)
                imported_count += 1
            
            print(f"✅ Imported {imported_count} jobs from CSV")
            self.save_jobs()
            
        except Exception as e:
            print(f"❌ Error importing CSV: {e}")
            print("Make sure CSV has columns: title, company, location, url, description")
    
    def save_jobs(self):
        """Save jobs to JSON file"""
        try:
            with open('data/saved_jobs.json', 'w') as f:
                json.dump(self.jobs, f, indent=2)
        except Exception as e:
            print(f"Error saving jobs: {e}")
    
    def load_jobs(self):
        """Load saved jobs from file"""
        try:
            if os.path.exists('data/saved_jobs.json'):
                with open('data/saved_jobs.json', 'r') as f:
                    self.jobs = json.load(f)
                    if self.jobs:
                        print(f"✅ Loaded {len(self.jobs)} saved jobs")
        except Exception as e:
            print(f"Error loading jobs: {e}")
            self.jobs = []
    
    def list_jobs(self):
        """Display all jobs"""
        if not self.jobs:
            print("❌ No jobs in the list. Add some first!")
            return
        
        print(f"\n📋 SAVED JOBS ({len(self.jobs)} total)")
        print("=" * 60)
        
        for i, job in enumerate(self.jobs, 1):
            print(f"\n{i}. {job['title']} at {job['company']}")
            print(f"   📍 Location: {job.get('location', 'Not specified')}")
            if job.get('salary'):
                print(f"   💰 Salary: {job['salary']}")
            if job.get('url'):
                print(f"   🔗 URL: {job['url'][:50]}...")
            print(f"   📅 Found: {job['date_found'][:10]}")
    
    def remove_job(self, job_index):
        """Remove a job from the list"""
        try:
            if 0 <= job_index < len(self.jobs):
                removed = self.jobs.pop(job_index)
                self.save_jobs()
                print(f"✅ Removed: {removed['title']} at {removed['company']}")
                return True
        except Exception as e:
            print(f"Error removing job: {e}")
        return False
    
    def search_tips(self):
        """Provide tips for finding jobs"""
        print("""
        🎯 JOB SEARCH TIPS:
        
        📍 Best Places to Search:
        • LinkedIn Jobs - linkedin.com/jobs
        • Indeed - indeed.com
        • AngelList (startups) - angel.co
        • Remote: RemoteOK, WeWorkRemotely
        • Tech: Dice, Built In, Hired
        • Entry Level: Handshake, WayUp
        
        🔍 Search Strategies:
        1. Use multiple variations of job titles
           (e.g., "Python Developer", "Backend Engineer", "Software Developer")
        2. Set up email alerts on job boards
        3. Follow companies you like on LinkedIn
        4. Use Boolean search (AND, OR, NOT)
        5. Check company career pages directly
        
        📝 Keywords to Include in Searches:
        • Your main programming languages
        • Specific frameworks/tools you know
        • Industry terms (fintech, SaaS, etc.)
        • Experience level (entry, junior, senior)
        
        ⏰ Best Times to Apply:
        • Apply within 24-48 hours of posting
        • Best days: Monday-Wednesday
        • Best time: Morning (9-11 AM) in company's timezone
        • Avoid: Late Friday or weekends
        
        🎯 Pro Tips:
        • Quality > Quantity (10 tailored > 50 generic)
        • Research the company before applying
        • Connect with employees on LinkedIn
        • Save jobs during the week, apply in batches
        • Track everything in this app!
        """)
    
    def create_job_csv_template(self):
        """Create a CSV template for bulk job import"""
        template_path = 'data/job_import_template.csv'
        
        import pandas as pd
        template = pd.DataFrame({
            'title': ['Python Developer', 'Data Analyst'],
            'company': ['Example Corp', 'Tech Startup'],
            'location': ['New York, NY', 'Remote'],
            'url': ['https://example.com/job1', 'https://example.com/job2'],
            'description': ['Python role with Django...', 'Analyze data using SQL...'],
            'salary': ['$80k-100k', '$70k-90k']
        })
        
        template.to_csv(template_path, index=False)
        print(f"✅ CSV template created: {template_path}")
        print("Edit this file and import it back to add multiple jobs at once!")