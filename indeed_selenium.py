from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime

def search_indeed_with_selenium(job_title, location):
    """Use Selenium to bypass Indeed's bot detection"""
    
    print("🌐 Starting browser for Indeed search...")
    
    # Setup Chrome options
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # Show browser window so you can see what's happening
    # options.add_argument('--headless')  # Uncomment to hide browser
    
    try:
        # Start browser
        print("🚀 Launching Chrome browser...")
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Go to Indeed Greece
        print("📍 Navigating to Indeed Greece...")
        driver.get("https://gr.indeed.com")
        time.sleep(3)
        
        # Accept cookies if prompted
        try:
            cookie_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_button.click()
            print("  ✓ Accepted cookies")
        except:
            pass
        
        # Search for jobs
        print(f"🔍 Searching for {job_title} in {location}...")
        
        # Find search boxes
        what_box = driver.find_element(By.ID, "text-input-what")
        what_box.clear()
        what_box.send_keys(job_title)
        
        where_box = driver.find_element(By.ID, "text-input-where")
        where_box.clear()
        where_box.send_keys(location)
        
        # Click search button
        search_button = driver.find_element(By.CLASS_NAME, "yosegi-InlineWhatWhere-primaryButton")
        search_button.click()
        
        # Wait for results
        time.sleep(5)
        
        # Get page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find job cards - Indeed uses different class names
        jobs = []
        
        # Try multiple selectors
        selectors = [
            'div.job_seen_beacon',
            'div.jobsearch-SerpJobCard',
            'div.slider_container',
            'div[data-jk]',
            'td.resultContent'
        ]
        
        job_cards = []
        for selector in selectors:
            job_cards = soup.select(selector)[:10]
            if job_cards:
                print(f"  ✓ Found job cards using selector: {selector}")
                break
        
        print(f"📊 Found {len(job_cards)} job cards")
        
        for card in job_cards:
            try:
                # Multiple ways to extract job info from Indeed's structure
                title = None
                company = None
                
                # Method 1: Direct selection
                title_elem = card.select_one('h2.jobTitle span[title]')
                if title_elem:
                    title = title_elem.get('title')
                
                # Method 2: Alternative title selection
                if not title:
                    title_elem = card.select_one('h2.jobTitle a span')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                
                # Method 3: Any span with title attribute
                if not title:
                    title_elem = card.select_one('span[title]')
                    if title_elem:
                        title = title_elem.get('title')
                
                # Extract company
                company_elem = card.select_one('span.companyName')
                if company_elem:
                    company = company_elem.get_text(strip=True)
                
                # Alternative company selector
                if not company:
                    company_elem = card.select_one('[data-testid="company-name"]')
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                
                # Extract location
                location_elem = card.select_one('div.companyLocation')
                job_location = location_elem.get_text(strip=True) if location_elem else location
                
                # Extract salary if available
                salary_elem = card.select_one('div.salary-snippet')
                salary = salary_elem.get_text(strip=True) if salary_elem else None
                
                # Only add if we got at least title or company
                if title or company:
                    job_data = {
                        'title': title or 'Title not found',
                        'company': company or 'Company not found',
                        'location': job_location,
                        'salary': salary,
                        'found_date': datetime.now().isoformat(),
                        'source': 'Indeed Greece'
                    }
                    jobs.append(job_data)
                    print(f"  ✓ Found: {title or 'Unknown'} at {company or 'Unknown'}")
                else:
                    print(f"  ⚠️ Could not extract job details from card")
                    # Debug: print what we got
                    print(f"     HTML preview: {str(card)[:200]}")
            
            except Exception as e:
                print(f"  ❌ Error extracting job: {e}")
                continue
        
        # Take screenshot for debugging
        driver.save_screenshot('data/indeed_screenshot.png')
        print("  📸 Screenshot saved to data/indeed_screenshot.png")
        
        driver.quit()
        return jobs
        
    except Exception as e:
        print(f"❌ Selenium error: {e}")
        return []

if __name__ == "__main__":
    # Try different searches
    searches = [
        ("Developer", "Thessaloniki"),
        ("Full stack Developer", "Thessaloniki"),
        ("AI Engineer", "Thessaloniki"),
        ("Python", "Thessaloniki"),
        ("Software Engineer", "Thessaloniki"),
        ("Προγραμματιστής", "Θεσσαλονίκη"),  # Greek terms
        ("IT", "Thessaloniki"),
        ("Data Engineer", "Thessaloniki"),
        ("Data Analyst", "Thessaloniki"),
        ("AI Engineer", "Thessaloniki")
    ]
    
    all_jobs = []
    for job_title, location in searches:
        print(f"\n🔍 Trying: {job_title} in {location}")
        jobs = search_indeed_with_selenium(job_title, location)
        all_jobs.extend(jobs)
        
        if jobs:
            break  # Found jobs, stop searching
    
    # At the end of the main section, after finding jobs:
    if all_jobs:
        print(f"\n✅ Total found: {len(all_jobs)} jobs!")
        
        # Save jobs to file
        import json
        filename = f'data/found_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_jobs, f, ensure_ascii=False, indent=2)
        print(f"💾 Jobs saved to: {filename}")
        
        for i, job in enumerate(all_jobs, 1):
            print(f"{i}. {job['title']} at {job['company']} ({job['location']})")
        else:
            print("\n❌ No jobs found on Indeed")
            print("\n💡 Try these alternatives:")
            print("1. Search on LinkedIn.com/jobs")
            print("2. Check Kariera.gr (Greek job site)")
            print("3. Try RemoteOK.io for remote jobs")
