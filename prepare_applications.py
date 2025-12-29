#!/usr/bin/env python3
"""
Prepare applications for jobs already found
No more CAPTCHA loops!
"""

import json
from datetime import datetime
from resume_tailor import ResumeTailor
from database import Database
import os

class ApplicationPreparer:
    def __init__(self):
        self.tailor = ResumeTailor()
        self.db = Database()
        
    def save_found_jobs(self, jobs):
        """Save jobs to JSON file"""
        filename = f'data/found_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {len(jobs)} jobs to: {filename}")
        return filename
    
    def load_latest_jobs(self):
        """Load the most recent jobs file"""
        import glob
        job_files = glob.glob('data/found_jobs_*.json')
        if not job_files:
            print("❌ No saved jobs found. Run indeed_selenium.py first!")
            return None
        
        latest_file = max(job_files)
        with open(latest_file, 'r', encoding='utf-8') as f:
            jobs = json.load(f)
        
        print(f"📂 Loaded {len(jobs)} jobs from: {latest_file}")
        return jobs
    
    def prepare_applications(self, jobs):
        """Generate tailored resumes and cover letters for jobs"""
        print(f"\n🎯 PREPARING APPLICATIONS FOR {len(jobs)} JOBS")
        print("=" * 60)
        
        applications = []
        
        for i, job in enumerate(jobs, 1):
            print(f"\n📝 {i}/{len(jobs)}: {job['title']} at {job['company']}")
            
            # Create a job description from what we have
            job_description = f"""
            Position: {job['title']}
            Company: {job['company']}
            Location: {job.get('location', 'Thessaloniki')}
            
            This is a {job['title']} position at {job['company']} based in {job.get('location', 'Thessaloniki')}.
            """
            
            try:
                # Generate tailored resume
                print("   ⏳ Tailoring resume...")
                tailored_resume = self.tailor.tailor_resume(
                    job_description=job_description,
                    company_name=job['company'],
                    position=job['title']
                )
                
                # Generate cover letter
                print("   ⏳ Generating cover letter...")
                cover_letter = self.tailor.generate_cover_letter(
                    job_description=job_description,
                    company_name=job['company'],
                    position=job['title']
                )
                
                # Save individual files
                safe_company = "".join(c for c in job['company'] if c.isalnum() or c in ' -_').strip()[:30]
                safe_title = "".join(c for c in job['title'] if c.isalnum() or c in ' -_').strip()[:30]
                
                resume_file = f"data/resumes/{i}_{safe_company}_{safe_title}_resume.txt"
                cover_file = f"data/resumes/{i}_{safe_company}_{safe_title}_cover.txt"
                
                os.makedirs('data/resumes', exist_ok=True)
                
                with open(resume_file, 'w', encoding='utf-8') as f:
                    f.write(tailored_resume)
                
                with open(cover_file, 'w', encoding='utf-8') as f:
                    f.write(cover_letter)
                
                # Log to database
                app_id = self.db.add_application(
                    company=job['company'],
                    position=job['title'],
                    location=job.get('location', 'Thessaloniki'),
                    resume=resume_file,
                    cover_letter=cover_file,
                    notes=f"Prepared on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                
                applications.append({
                    'app_id': app_id,
                    'job': job,
                    'resume_file': resume_file,
                    'cover_file': cover_file
                })
                
                print(f"   ✅ Application #{app_id} prepared")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        # Save summary
        summary_file = f'data/application_batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(applications, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ COMPLETE!")
        print(f"📊 Prepared: {len(applications)}/{len(jobs)} applications")
        print(f"📁 Files saved in: data/resumes/")
        print(f"📋 Summary saved to: {summary_file}")
        
        return applications

def main():
    # The jobs from your indeed_selenium.py run
    jobs_from_search = [
        {'title': 'Junior Java Web Developer / Tester (Remote/Thessaloniki)', 'company': 'EUROPEAN DYNAMICS', 'location': 'Thessaloniki'},
        {'title': 'Fullstack Developer', 'company': 'DOTSOFT SA', 'location': 'Thessaloniki'},
        {'title': 'Fullstack Javascript Developer', 'company': 'Aylo Careers', 'location': 'Thessaloniki'},
        {'title': 'Junior QA Engineer', 'company': 'EUROPEAN DYNAMICS', 'location': 'Thessaloniki'},
        {'title': 'Java Software Developer', 'company': 'Travelfusion Ltd.', 'location': 'Thessaloniki'},
        {'title': 'Junior/Mid Android Developer - Hybrid', 'company': 'Schoox, LLC', 'location': 'Thessaloniki'},
        {'title': 'QA Engineer - Automation & Manual (Remote/Thessaloniki)', 'company': 'EUROPEAN DYNAMICS', 'location': 'Thessaloniki'},
        {'title': 'Mid-Level Full Stack PHP Developer', 'company': 'Artion Medical Software', 'location': 'Thessaloniki'},
    ]
    
    print("""
    ╔════════════════════════════════════════════════════╗
    ║   📝 APPLICATION PREPARATION SYSTEM                ║
    ║   No CAPTCHAs, Just Results!                      ║
    ╚════════════════════════════════════════════════════╝
    """)
    
    preparer = ApplicationPreparer()
    
    # Save the jobs
    preparer.save_found_jobs(jobs_from_search)
    
    # Prepare applications
    print("\nPreparing tailored applications for all found jobs...")
    applications = preparer.prepare_applications(jobs_from_search)
    
    if applications:
        print(f"""
        ╔════════════════════════════════════════════════════╗
        ║   ✅ SUCCESS!                                      ║
        ╚════════════════════════════════════════════════════╝
        
        WHAT YOU HAVE NOW:
        ==================
        • {len(applications)} tailored resumes ready
        • {len(applications)} custom cover letters ready
        • All saved in: data/resumes/
        
        HOW TO APPLY:
        =============
        1. Go to Indeed.com
        2. Search for each company/position
        3. Click "Apply"
        4. Copy/paste your tailored resume & cover letter
        5. Submit!
        
        YOUR APPLICATIONS:
        ==================
        """)
        
        for i, app in enumerate(applications, 1):
            print(f"{i}. {app['job']['title']}")
            print(f"   Company: {app['job']['company']}")
            print(f"   Resume: {app['resume_file']}")
            print(f"   Cover: {app['cover_file']}")
            print()

if __name__ == "__main__":
    main()