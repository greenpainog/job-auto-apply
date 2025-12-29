#!/usr/bin/env python3
"""
Auto Apply Bot - Automatically apply to jobs matching your criteria
"""

from auto_applier import JobAutoApplier
from job_scraper import JobScraper
import json
import time
from datetime import datetime
import schedule
import os

class AutoApplyBot:
    def __init__(self):
        # Load configuration
        with open('auto_apply_config.json', 'r') as f:
            self.config = json.load(f)
        
        self.applier = JobAutoApplier(
            email=self.config['email'],
            email_password=self.config['email_password']
        )
        
        self.applier.keywords = self.config['keywords']
        self.applier.locations = self.config['locations']
        self.applier.exclude_companies = self.config.get('exclude_companies', [])
        self.applier.min_salary = self.config.get('min_salary')
    
    def run_job_search_and_apply(self):
        """Main job search and apply process"""
        print(f"\n{'='*50}")
        print(f"🤖 AUTO-APPLY BOT RUN - {datetime.now()}")
        print(f"{'='*50}")
        
        # Search for jobs
        scraper = JobScraper()
        
        # Search different sources
        for keyword in self.config['keywords']:
            scraper.scrape_remote_ok([keyword])
            time.sleep(5)  # Be respectful
        
        # Apply to matching jobs
        for job in scraper.jobs:
            if self.should_apply(job):
                self.apply_to_job(job)
                time.sleep(60)  # Wait 1 minute between applications
    
    def should_apply(self, job):
        """Check if we should apply to this job"""
        # Check if already applied
        job_id = f"{job['company']}_{job['title']}"
        if job_id in self.applier.applied_jobs:
            return False
        
        # Check salary if specified
        if self.applier.min_salary and job.get('salary'):
            if job['salary'] < self.applier.min_salary:
                return False
        
        return True
    
    def apply_to_job(self, job):
        """Apply to a specific job"""
        print(f"\n🎯 Applying to: {job['title']} at {job['company']}")
        
        # If email application available
        if job.get('apply_email'):
            resume_path = self.config['resume_path']
            self.applier.auto_apply_email(job, resume_path)
        
        # If URL only, log it for manual application
        else:
            with open('data/manual_apply_queue.json', 'a') as f:
                json.dump({
                    'job': job,
                    'timestamp': datetime.now().isoformat()
                }, f)
                f.write('\n')
            print(f"📋 Added to manual apply queue: {job['url']}")
    
    def run_scheduled(self):
        """Run on schedule"""
        # Schedule runs
        schedule.every(4).hours.do(self.run_job_search_and_apply)
        
        print("🤖 Auto-Apply Bot Started!")
        print(f"Will run every 4 hours")
        print(f"Keywords: {self.config['keywords']}")
        print(f"Locations: {self.config['locations']}")
        
        # Run once immediately
        self.run_job_search_and_apply()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    # Create config file if it doesn't exist
    config_path = 'auto_apply_config.json'
    
    if not os.path.exists(config_path):
        config = {
            "email": "angelis.chatziantoniou@gmail.com",
            "email_password": "your_app_password",
            "keywords": ["Python Developer", "Software Engineer", "Backend Developer","AI Engineer"],
            "locations": ["Remote", "Thessaloniki", "Central Macedonia"],
            "exclude_companies": [],
            "min_salary": 1000,
            "resume_path": "data/Evangelos_Chatziantoniou_CV.pdf",
            "max_daily_applications": 10
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("📝 Created auto_apply_config.json - Please edit it with your details!")
        exit()
    
    # Run the bot
    bot = AutoApplyBot()
    bot.run_scheduled()