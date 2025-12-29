#!/usr/bin/env python3
"""
Semi-automated job application system
Searches for jobs, prepares applications, but lets you handle CAPTCHAs
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import json
from resume_tailor import ResumeTailor
from database import Database

class SemiAutoApply:
    def __init__(self):
        self.tailor = ResumeTailor()
        self.db = Database()
        self.jobs_found = []
        
    def search_indeed_semi_auto(self):
        """Search Indeed with manual CAPTCHA solving"""
        print("\n🌐 SEMI-AUTOMATED INDEED SEARCH")
        print("=" * 50)
        print("ℹ️ I'll help you search, but you handle CAPTCHAs!")
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Keep browser visible so user can solve CAPTCHA
        
        driver = webdriver.Chrome(options=options)
        
        try:
            # Go to Indeed
            driver.get("https://gr.indeed.com")
            
            print("\n📝 INSTRUCTIONS:")
            print("1. I'll fill in the search fields")
            print("2. You solve any CAPTCHA if it appears")
            print("3. Press Enter here when ready")
            
            # Search for jobs
            search_terms = [
                ("Developer", "Thessaloniki"),
                ("Python", "Remote Greece"),
                ("Software Engineer", "Thessaloniki")
            ]
            
            for job_title, location in search_terms:
                print(f"\n🔍 Searching: {job_title} in {location}")
                
                # Navigate to search page
                driver.get(f"https://gr.indeed.com/jobs?q={job_title}&l={location}")
                
                # Wait for user to handle CAPTCHA if needed
                input("   ⏸️ Solve CAPTCHA if shown, then press Enter...")
                
                # Now extract jobs from the page
                jobs = self.extract_jobs_from_page(driver)
                self.jobs_found.extend(jobs)
                
                if len(self.jobs_found) >= 10:
                    break
            
            print(f"\n✅ Total jobs found: {len(self.jobs_found)}")
            
        finally:
            driver.quit()
        
        return self.jobs_found
    
    def extract_jobs_from_page(self, driver):
        """Extract job details from current Indeed page"""
        jobs = []
        
        try:
            # Get all job cards
            job_elements = driver.find_elements(By.CSS_SELECTOR, '.job_seen_beacon')
            
            for element in job_elements[:10]:
                try:
                    # Extract with Selenium (more reliable than BeautifulSoup for dynamic content)
                    title = element.find_element(By.CSS_SELECTOR, 'h2.jobTitle span').text
                    company = element.find_element(By.CSS_SELECTOR, '.companyName').text
                    location = element.find_element(By.CSS_SELECTOR, '.companyLocation').text
                    
                    # Try to get salary
                    try:
                        salary = element.find_element(By.CSS_SELECTOR, '.salary-snippet').text
                    except:
                        salary = None
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'source': 'Indeed'
                    }
                    
                    jobs.append(job)
                    print(f"   ✓ Found: {title} at {company}")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"   ❌ Error extracting jobs: {e}")
        
        return jobs
    
    def prepare_applications(self):
        """Generate tailored resumes for found jobs"""
        if not self.jobs_found:
            print("❌ No jobs to prepare applications for")
            return
        
        print(f"\n📝 PREPARING APPLICATIONS")
        print("=" * 50)
        
        applications = []
        
        for i, job in enumerate(self.jobs_found[:5], 1):  # Prepare first 5
            print(f"\n{i}. Preparing for: {job['title']} at {job['company']}")
            
            # Generate tailored resume
            tailored_resume = self.tailor.tailor_resume(
                job_description=job.get('title', ''),
                company_name=job['company'],
                position=job['title']
            )
            
            # Generate cover letter
            cover_letter = self.tailor.generate_cover_letter(
                job_description=job.get('title', ''),
                company_name=job['company'],
                position=job['title']
            )
            
            # Save to database
            app_id = self.db.add_application(
                company=job['company'],
                position=job['title'],
                location=job.get('location'),
                salary_range=job.get('salary'),
                notes="Found via semi-automated search"
            )
            
            applications.append({
                'job': job,
                'tailored_resume': tailored_resume,
                'cover_letter': cover_letter,
                'app_id': app_id
            })
            
            print(f"   ✅ Application #{app_id} prepared")
        
        # Save applications to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/prepared_applications_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(applications, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Applications saved to: {filename}")
        print(f"📋 Total applications prepared: {len(applications)}")
        
        return applications

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║   🤖 SEMI-AUTOMATED JOB APPLICATION        ║
    ║   You handle CAPTCHAs, I do the rest!      ║
    ╚════════════════════════════════════════════╝
    """)
    
    applier = SemiAutoApply()
    
    # Step 1: Search for jobs
    jobs = applier.search_indeed_semi_auto()
    
    if jobs:
        # Step 2: Prepare applications
        print("\n" + "="*50)
        prepare = input("Prepare tailored applications for these jobs? (y/n): ")
        
        if prepare.lower() == 'y':
            applications = applier.prepare_applications()
            
            print(f"""
            \n✅ SUCCESS! 
            =====================================
            Jobs Found: {len(jobs)}
            Applications Prepared: {len(applications) if applications else 0}
            
            Next Steps:
            1. Review prepared applications in data/
            2. Go to Indeed and apply to each job
            3. Use the tailored resume & cover letter
            =====================================
            """)
    else:
        print("\n❌ No jobs found")

if __name__ == "__main__":
    main()