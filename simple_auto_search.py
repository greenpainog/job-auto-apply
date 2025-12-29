#!/usr/bin/env python3
"""
Simple job search without email sending
"""

from auto_applier import JobAutoApplier
import json

def main():
    # Load config
    with open('auto_apply_config.json', 'r') as f:
        config = json.load(f)
    
    # Create applier (without email for now)
    applier = JobAutoApplier(
        email=config['email'],
        email_password="not_needed_for_search_only"
    )
    
    # Set criteria
    applier.keywords = config['keywords']
    applier.locations = config['locations']
    applier.exclude_companies = config.get('exclude_companies', [])
    applier.min_salary = config.get('min_salary', 0)
    
    # Search for jobs (without applying)
    print("🔍 Starting job search...")
    
    # Search for Python Developer in Thessaloniki
    jobs = applier.search_jobs_indeed("Python Developer", "Thessaloniki Greece")
    
    if jobs:
        print(f"\n📋 Found {len(jobs)} jobs!")
        for job in jobs:
            print(f"\n• {job['title']} at {job['company']}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  Salary: {job.get('salary', 'Not specified')}")
    else:
        print("No jobs found. Try different search terms.")

if __name__ == "__main__":
    main()