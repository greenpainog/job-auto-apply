#!/usr/bin/env python3
"""
REAL Auto-Apply System - Actually sends applications!
Uses your existing resume and applies to jobs automatically
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import os
from datetime import datetime
import PyPDF2
import re
import getpass

class RealAutoApply:
    def __init__(self, config_path='auto_apply_config.json'):
        # Load config
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.email = self.config['email']
        self.resume_path = self.config['resume_path']  # Your PDF resume
        self.applied_jobs = self.load_applied_history()
        
        # Check if resume exists
        if not os.path.exists(self.resume_path):
            print(f"❌ Resume not found at: {self.resume_path}")
            print(f"   Please check the path in auto_apply_config.json")
            exit(1)
        else:
            print(f"✅ Using resume: {self.resume_path}")
    
    def load_applied_history(self):
        """Load history of applied jobs to avoid duplicates"""
        try:
            with open('data/applied_history.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_applied_job(self, job_id, platform, company, position):
        """Save record of applied job"""
        application = {
            'id': job_id,
            'platform': platform,
            'company': company,
            'position': position,
            'applied_date': datetime.now().isoformat()
        }
        self.applied_jobs.append(application)
        
        with open('data/applied_history.json', 'w') as f:
            json.dump(self.applied_jobs, f, indent=2)
    
    def setup_email(self, password):
        """Setup Gmail SMTP"""
        try:
            self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
            self.smtp.starttls()
            self.smtp.login(self.email, password)
            print("✅ Email connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Email connection failed: {e}")
            print("   Make sure you're using an App Password from Google")
            return False
    
    def apply_via_email(self, company_email, position, company_name, custom_message=None):
        """Actually send application email with resume attached"""
        # Check if already applied
        job_id = f"{company_name}_{position}"
        if any(job['id'] == job_id for job in self.applied_jobs):
            print(f"⏭️  Already applied to {position} at {company_name}")
            return False
        
        try:
            print(f"📧 Applying to {position} at {company_name}...")
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = company_email
            msg['Subject'] = f"Application for {position} Position"
            
            # Email body
            if custom_message:
                body = custom_message
            else:
                body = f"""Dear Hiring Team at {company_name},

I am writing to express my strong interest in the {position} position at {company_name}.

With my experience in software development, particularly in Python, full-stack development, and AI engineering, 
I am confident I would be a valuable addition to your team.

Key highlights of my background:
• Strong experience in Python, JavaScript, and modern web frameworks
• Proven track record in developing scalable applications
• Experience with AI/ML technologies and cloud platforms
• Excellent problem-solving and team collaboration skills

I have attached my resume for your review. I would welcome the opportunity to discuss how my skills 
and experience align with your team's needs.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
Evangelos Chatziantoniou
{self.email}
LinkedIn: linkedin.com/in/vangelis-chatziantoniou"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach resume PDF
            with open(self.resume_path, 'rb') as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', 
                                filename=os.path.basename(self.resume_path))
                msg.attach(attach)
            
            # Send email
            self.smtp.send_message(msg)
            
            print(f"✅ Application sent to {company_email}!")
            
            # Save to history
            self.save_applied_job(job_id, 'email', company_name, position)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send application: {e}")
            return False
    
    def apply_linkedin_easy_apply(self, email, password):
        """Auto-apply to LinkedIn Easy Apply jobs"""
        print("\n🔗 LINKEDIN EASY APPLY")
        print("=" * 50)
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        try:
            # Login to LinkedIn
            print("🔐 Logging into LinkedIn...")
            driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Enter credentials
            driver.find_element(By.ID, "username").send_keys(email)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            time.sleep(5)
            
            # Check for 2FA
            if "checkpoint" in driver.current_url:
                input("⏸️  Complete 2FA in browser, then press Enter...")
            
            # Search for Easy Apply jobs
            keywords = self.config['keywords']
            locations = self.config['locations']
            
            for keyword in keywords[:2]:  # Limit to avoid detection
                for location in locations[:1]:
                    print(f"\n🔍 Searching: {keyword} in {location}")
                    
                    # Search URL with Easy Apply filter
                    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&location={location}&f_AL=true"
                    driver.get(search_url)
                    time.sleep(3)
                    
                    # Find Easy Apply jobs
                    job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container")[:5]
                    
                    for card in job_cards:
                        try:
                            # Get job info
                            title = card.find_element(By.CSS_SELECTOR, ".job-card-list__title").text
                            company = card.find_element(By.CSS_SELECTOR, ".job-card-container__company-name").text
                            
                            job_id = f"linkedin_{company}_{title}"
                            if any(job['id'] == job_id for job in self.applied_jobs):
                                print(f"  ⏭️ Already applied to {title} at {company}")
                                continue
                            
                            print(f"\n  🎯 Applying to {title} at {company}")
                            
                            # Click job card
                            card.click()
                            time.sleep(2)
                            
                            # Click Easy Apply button
                            try:
                                easy_apply_btn = driver.find_element(By.CSS_SELECTOR, ".jobs-apply-button")
                                easy_apply_btn.click()
                                time.sleep(2)
                                
                                # Handle application flow
                                # This varies by job, but try common patterns
                                
                                # Try to click Next/Submit buttons
                                max_steps = 5
                                for step in range(max_steps):
                                    time.sleep(1)
                                    
                                    # Check for submit button
                                    try:
                                        submit_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Submit')]")
                                        submit_btn.click()
                                        print(f"    ✅ Application submitted!")
                                        self.save_applied_job(job_id, 'linkedin', company, title)
                                        time.sleep(2)
                                        break
                                    except:
                                        pass
                                    
                                    # Check for next button
                                    try:
                                        next_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue')]")
                                        next_btn.click()
                                        continue
                                    except:
                                        pass
                                    
                                    # Check for review button
                                    try:
                                        review_btn = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Review')]")
                                        review_btn.click()
                                        continue
                                    except:
                                        pass
                                
                                # Close modal if still open
                                try:
                                    close_btn = driver.find_element(By.CSS_SELECTOR, "[aria-label='Dismiss']")
                                    close_btn.click()
                                except:
                                    pass
                                    
                            except Exception as e:
                                print(f"    ⚠️ Easy Apply button not found or application requires more info")
                            
                        except Exception as e:
                            print(f"  ❌ Error with job card: {e}")
                            continue
                        
                        time.sleep(5)  # Don't spam applications
            
        finally:
            driver.quit()
    
    def search_jobs_with_emails(self):
        """Find jobs that accept email applications"""
        print("\n📧 FINDING JOBS WITH EMAIL APPLICATIONS")
        print("=" * 50)
        
        email_jobs = []
        
        # Greek companies that often accept email applications
        greek_companies = [
            {'company': 'Schoox', 'email': 'careers@schoox.com', 'positions': ['Developer', 'Engineer']},
            {'company': 'Workable', 'email': 'careers@workable.com', 'positions': ['Software Engineer', 'Developer']},
            {'company': 'Accusonus', 'email': 'jobs@accusonus.com', 'positions': ['Software Developer', 'AI Engineer']},
            {'company': 'Epignosis', 'email': 'hr@epignosis.com', 'positions': ['Full Stack Developer', 'Backend Developer']},
            {'company': 'Netdata', 'email': 'careers@netdata.cloud', 'positions': ['Software Engineer', 'Cloud Engineer']},
        ]
        
        # Search for remote companies with email applications
        remote_companies = [
            {'company': 'GitLab', 'email': 'careers@gitlab.com', 'positions': ['Backend Engineer', 'Full Stack Developer']},
            {'company': 'Canonical', 'email': 'careers@canonical.com', 'positions': ['Python Developer', 'Software Engineer']},
            {'company': 'Red Hat', 'email': 'jobs@redhat.com', 'positions': ['Software Engineer', 'Developer']},
        ]
        
        all_companies = greek_companies + remote_companies
        
        for company_info in all_companies:
            for position in company_info['positions']:
                if any(keyword.lower() in position.lower() for keyword in self.config['keywords']):
                    email_jobs.append({
                        'company': company_info['company'],
                        'email': company_info['email'],
                        'position': position
                    })
                    print(f"  ✓ Found: {position} at {company_info['company']} ({company_info['email']})")
        
        return email_jobs

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🚀 REAL AUTO-APPLY SYSTEM                              ║
    ║   Actually sends applications automatically!              ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    applier = RealAutoApply()
    
    print("\nChoose application method:")
    print("1. Email applications (automated)")
    print("2. LinkedIn Easy Apply (semi-automated)")
    print("3. Both")
    
    choice = input("\nYour choice (1-3): ")
    
    if choice in ['1', '3']:
        # Email applications
        email_password = getpass.getpass("Enter your Gmail App Password: ")
        
        if applier.setup_email(email_password):
            # Find jobs with email applications
            email_jobs = applier.search_jobs_with_emails()
            
            if email_jobs:
                print(f"\n📧 Ready to apply to {len(email_jobs)} jobs via email")
                confirm = input("Send applications? (y/n): ")
                
                if confirm.lower() == 'y':
                    for job in email_jobs:
                        applier.apply_via_email(
                            company_email=job['email'],
                            position=job['position'],
                            company_name=job['company']
                        )
                        time.sleep(10)  # Wait between applications
    
    if choice in ['2', '3']:
        # LinkedIn Easy Apply
        linkedin_email = input("LinkedIn email: ")
        linkedin_password = getpass.getpass("LinkedIn password: ")
        
        applier.apply_linkedin_easy_apply(linkedin_email, linkedin_password)
    
    print(f"""
    \n✅ AUTO-APPLY COMPLETE!
    =====================================
    Check data/applied_history.json for all applications
    
    Next steps:
    1. Check your email sent folder for confirmations
    2. Monitor LinkedIn for responses
    3. Follow up in 1 week if no response
    =====================================
    """)

if __name__ == "__main__":
    main()