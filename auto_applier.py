import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import time
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from resume_tailor import ResumeTailor
from database import Database

class JobAutoApplier:
    def __init__(self, email, email_password):
        self.email = email
        self.email_password = email_password
        self.db = Database()
        self.tailor = ResumeTailor()
        self.applied_jobs = self.load_applied_jobs()
        
        # Your criteria
        self.keywords = []
        self.locations = []
        self.exclude_companies = []
        self.min_salary = None
        
    def load_applied_jobs(self):
        """Load list of already applied jobs to avoid duplicates"""
        try:
            with open('data/applied_jobs.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_applied_job(self, job_id):
        """Save applied job to avoid reapplying"""
        self.applied_jobs.append(job_id)
        with open('data/applied_jobs.json', 'w') as f:
            json.dump(self.applied_jobs, f)
    
    def setup_email(self):
        """Setup SMTP for sending emails"""
        # For Gmail
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.starttls()
        self.smtp.login(self.email, self.email_password)
    
    def search_jobs_indeed(self, job_title, location):
        """Search Indeed with anti-bot detection measures"""
        jobs = []
        
        # Format search
        job_title_formatted = job_title.replace(' ', '+')
        location_formatted = location.replace(' ', '+')
        
        # Try different Indeed domains
        base_urls = [
            "https://gr.indeed.com",  # Greece
            "https://www.indeed.com"   # International
        ]
        
        # More realistic headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Use session to maintain cookies
        import requests
        session = requests.Session()
        session.headers.update(headers)
        
        for base_url in base_urls:
            try:
                # First visit the homepage to get cookies
                print(f"🔍 Visiting Indeed homepage first...")
                homepage_response = session.get(base_url, timeout=10)
                time.sleep(2)  # Wait a bit
                
                # Now search
                url = f"{base_url}/jobs?q={job_title_formatted}&l={location_formatted}"
                print(f"🔍 Searching: {url}")
                
                response = session.get(url, timeout=10)
                
                if response.status_code == 403:
                    print(f"  ⚠️ Indeed is blocking requests (403). Trying alternative method...")
                    continue
                
                if response.status_code != 200:
                    print(f"  ⚠️ Got status code: {response.status_code}")
                    continue
                
                print(f"  ✅ Got response from Indeed")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Indeed's structure - try multiple selectors
                job_cards = (
                    soup.find_all('div', {'class': 'job_seen_beacon'}) or
                    soup.find_all('div', {'class': 'jobsearch-SerpJobCard'}) or
                    soup.find_all('div', {'class': 'slider_container'}) or
                    soup.find_all('div', {'class': 'cardOutline'}) or
                    soup.find_all('div', {'id': lambda x: x and 'job_' in x})
                )
                
                if not job_cards:
                    print("  ⚠️ No job cards found with known selectors")
                    # Save for debugging
                    with open('data/indeed_page.html', 'w', encoding='utf-8') as f:
                        f.write(response.text[:10000])  # Save first 10k chars
                    print("  💾 Saved page snippet to data/indeed_page.html")
                
                for card in job_cards[:10]:
                    try:
                        # Extract job details with multiple attempts
                        title = (
                            card.find('h2', {'class': 'jobTitle'}) or
                            card.find('a', {'data-testid': 'job-title'}) or
                            card.find('span', {'title': True})
                        )
                        
                        company = (
                            card.find('span', {'class': 'companyName'}) or
                            card.find('div', {'class': 'companyName'}) or
                            card.find('a', {'data-testid': 'company-name'})
                        )
                        
                        if title and company:
                            title_text = title.get_text(strip=True)
                            company_text = company.get_text(strip=True)
                            
                            job = {
                                'id': f"{company_text}_{title_text}_{datetime.now().date()}",
                                'title': title_text,
                                'company': company_text,
                                'location': location,
                                'description': card.get_text(strip=True)[:300],
                                'source': 'Indeed'
                            }
                            jobs.append(job)
                            print(f"  ✓ Found: {title_text} at {company_text}")
                    
                    except Exception as e:
                        continue
                
                if jobs:
                    break  # Found jobs, stop trying other domains
                    
            except requests.exceptions.Timeout:
                print(f"  ⚠️ Request timed out")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print(f"📊 Found {len(jobs)} jobs total")
        return jobs

    def search_jobs_with_emails(self):
        """Search multiple sources for jobs with email applications"""
        all_jobs = []
        
        # Search various sites
        print("🔍 Searching for jobs with email applications...")
        
        # 1. Search AngelList/Wellfound (startups often use email)
        # 2. Search RemoteOK (remote jobs often use email)
        # 3. Search company career pages directly
        
        # For now, using a simple approach
        # In production, you'd want to use proper APIs
        
        return all_jobs
    
    def matches_criteria(self, job):
        """Check if job matches your criteria"""
        # Check keywords
        if self.keywords:
            job_text = f"{job['title']} {job['description']}".lower()
            if not any(keyword.lower() in job_text for keyword in self.keywords):
                return False
        
        # Check excluded companies
        if job['company'] in self.exclude_companies:
            return False
        
        # Check if already applied
        if job['id'] in self.applied_jobs:
            print(f"⏭️ Already applied to {job['title']} at {job['company']}")
            return False
        
        return True
    
    def auto_apply_email(self, job, resume_path, cover_letter=None):
        """Automatically send application email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = job['email']
            msg['Subject'] = f"Application for {job['title']} Position"
            
            # Generate tailored cover letter
            if not cover_letter:
                cover_letter = self.tailor.generate_cover_letter(
                    job['description'],
                    job['company'],
                    job['title']
                )
            
            # Email body
            body = cover_letter
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach resume
            with open(resume_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', 
                                filename=os.path.basename(resume_path))
                msg.attach(attach)
            
            # Send email
            self.smtp.send_message(msg)
            
            print(f"✅ Applied to {job['title']} at {job['company']}")
            
            # Log application
            self.db.add_application(
                company=job['company'],
                position=job['title'],
                notes=f"Auto-applied via email to {job['email']}"
            )
            
            # Save to avoid reapplying
            self.save_applied_job(job['id'])
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply to {job['title']}: {e}")
            return False
    
    def auto_apply_linkedin_easy(self, job_urls):
        """Automate LinkedIn Easy Apply (requires LinkedIn login)"""
        driver = webdriver.Chrome()  # You need ChromeDriver installed
        
        try:
            # Login to LinkedIn
            driver.get("https://www.linkedin.com/login")
            
            email_input = driver.find_element(By.ID, "username")
            email_input.send_keys(self.email)
            
            password_input = driver.find_element(By.ID, "password")
            password_input.send_keys(input("Enter LinkedIn password: "))
            
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            time.sleep(5)  # Wait for login
            
            for job_url in job_urls:
                try:
                    driver.get(job_url)
                    time.sleep(3)
                    
                    # Click Easy Apply button
                    easy_apply_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
                    easy_apply_btn.click()
                    
                    time.sleep(2)
                    
                    # Fill out application (this varies by job)
                    # You'd need to handle different form types
                    
                    # Submit
                    submit_btn = driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
                    submit_btn.click()
                    
                    print(f"✅ Applied via LinkedIn Easy Apply")
                    time.sleep(5)  # Don't spam
                    
                except Exception as e:
                    print(f"❌ Failed to apply: {e}")
                    continue
                    
        finally:
            driver.quit()
    
    def run_auto_apply(self, job_title, location, max_applications=10):
        """Main auto-apply process"""
        print(f"""
        🚀 AUTO-APPLY BOT STARTED
        ============================
        Job Title: {job_title}
        Location: {location}
        Max Applications: {max_applications}
        ============================
        """)
        
        # Setup email
        self.setup_email()
        
        # Search for jobs
        jobs = self.search_jobs_indeed(job_title, location)
        
        # Filter jobs
        matching_jobs = [job for job in jobs if self.matches_criteria(job)]
        
        print(f"\n📊 Found {len(matching_jobs)} matching jobs")
        
        # Apply to jobs
        applications_sent = 0
        for job in matching_jobs[:max_applications]:
            print(f"\n🎯 Applying to: {job['title']} at {job['company']}")
            
            # Generate tailored resume
            tailored_resume = self.tailor.tailor_resume(
                job['description'],
                job['company'],
                job['title']
            )
            
            # Save tailored resume as PDF (you'd need to implement PDF conversion)
            resume_path = f"data/resumes/auto_{job['company']}_{datetime.now().strftime('%Y%m%d')}.txt"
            with open(resume_path, 'w') as f:
                f.write(tailored_resume)
            
            # Apply
            if self.auto_apply_email(job, resume_path):
                applications_sent += 1
            
            # Don't spam - wait between applications
            time.sleep(30)
        
        print(f"""
        ✅ AUTO-APPLY COMPLETE
        ============================
        Applications Sent: {applications_sent}
        ============================
        """)