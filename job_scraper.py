import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

class JobScraper:
    def __init__(self):
        self.jobs = []
    
    def scrape_remote_ok(self, keywords):
        """Scrape RemoteOK for remote jobs"""
        url = f"https://remoteok.io/api"
        
        try:
            response = requests.get(url)
            jobs_data = response.json()
            
            for job in jobs_data[1:20]:  # Skip first item (metadata)
                if any(kw.lower() in job.get('position', '').lower() for kw in keywords):
                    self.jobs.append({
                        'title': job.get('position'),
                        'company': job.get('company'),
                        'url': job.get('url'),
                        'description': job.get('description'),
                        'apply_url': job.get('apply_url'),
                        'date': job.get('date'),
                        'salary': job.get('salary_min'),
                        'tags': job.get('tags', [])
                    })
            
            print(f"✅ Found {len(self.jobs)} jobs on RemoteOK")
            
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
    
    def scrape_ycombinator(self):
        """Scrape Y Combinator jobs"""
        url = "https://www.ycombinator.com/jobs/role/software-engineer"
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_listings = soup.find_all('a', class_='job-listing')
            
            for listing in job_listings[:10]:
                self.jobs.append({
                    'title': listing.find('h3').text.strip(),
                    'company': listing.find('div', class_='company').text.strip(),
                    'url': f"https://www.ycombinator.com{listing['href']}",
                    'description': listing.text.strip()
                })
            
            print(f"✅ Found {len(job_listings)} jobs on YC")
            
        except Exception as e:
            print(f"Error scraping YC: {e}")
    
    def use_adzuna_api(self, what, where, api_id, api_key):
        """Use Adzuna API (free tier available)"""
        url = f"https://api.adzuna.com/v1/api/jobs/us/search/1"
        
        params = {
            'app_id': api_id,
            'app_key': api_key,
            'what': what,
            'where': where,
            'results_per_page': 20
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            for job in data.get('results', []):
                self.jobs.append({
                    'title': job.get('title'),
                    'company': job.get('company', {}).get('display_name'),
                    'url': job.get('redirect_url'),
                    'description': job.get('description'),
                    'salary': job.get('salary_min'),
                    'location': job.get('location', {}).get('display_name')
                })
            
            print(f"✅ Found {len(self.jobs)} jobs via Adzuna API")
            
        except Exception as e:
            print(f"Error using Adzuna API: {e}")