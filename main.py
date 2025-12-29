#!/usr/bin/env python3
"""
Job Application Assistant
Your personal assistant for managing job applications
"""

import os
import sys
from datetime import datetime, timedelta
from database import Database
from resume_tailor import ResumeTailor
from job_finder import JobFinder
from config import Config

class JobApplicationAssistant:
    def __init__(self):
        print("\n🚀 Initializing Job Application Assistant...")
        self.db = Database()
        self.tailor = ResumeTailor()
        self.finder = JobFinder()
        
        print("✅ Ready to help you land your dream job!")
        print("=" * 60)
    
    def display_menu(self):
        """Show main menu"""
        stats = self.db.get_stats()
        
        print("\n" + "="*60)
        print("📊 Quick Stats: Total Applications: {} | This Week: {}".format(
            stats['total'], stats['this_week']
        ))
        print("="*60)
        print("\n📋 MAIN MENU")
        print("-" * 30)
        print("1. 🔍 Job Search & Management")
        print("2. 📝 Apply to a Job") 
        print("3. 📊 View Applications")
        print("4. 📄 Resume Management")
        print("5. 📈 Application Statistics")
        print("6. 💡 Job Search Tips")
        print("7. 🚪 Exit")
        print("-" * 30)
        
        return input("\nChoose an option (1-7): ").strip()
    
    def job_search_menu(self):
        """Job search submenu"""
        while True:
            print("\n🔍 JOB SEARCH & MANAGEMENT")
            print("-" * 30)
            print("1. Add job manually")
            print("2. List saved jobs")
            print("3. Remove a job")
            print("4. Import jobs from CSV")
            print("5. Create CSV template")
            print("6. Back to main menu")
            
            choice = input("\nChoose option (1-6): ").strip()
            
            if choice == '1':
                self.finder.manual_add_job()
            elif choice == '2':
                self.finder.list_jobs()
            elif choice == '3':
                self.finder.list_jobs()
                if self.finder.jobs:
                    try:
                        job_num = int(input("\nEnter job number to remove: ")) - 1
                        self.finder.remove_job(job_num)
                    except ValueError:
                        print("Invalid input")
            elif choice == '4':
                csv_path = input("Enter CSV file path: ")
                self.finder.import_from_csv(csv_path)
            elif choice == '5':
                self.finder.create_job_csv_template()
            elif choice == '6':
                break
    
    def apply_to_job(self):
        """Apply to a job with tailored resume"""
        print("\n🎯 APPLY TO JOB")
        print("-" * 40)
        
        # Option to select from saved jobs
        if self.finder.jobs:
            use_saved = input("\nSelect from saved jobs? (y/n): ").lower()
            if use_saved == 'y':
                self.finder.list_jobs()
                try:
                    job_num = int(input("\nEnter job number: ")) - 1
                    if 0 <= job_num < len(self.finder.jobs):
                        job = self.finder.jobs[job_num]
                        company = job['company']
                        position = job['title']
                        job_url = job.get('url', '')
                        job_description = job.get('description', '')
                        location = job.get('location', '')
                    else:
                        print("Invalid job number")
                        return
                except ValueError:
                    print("Invalid input")
                    return
            else:
                # Manual entry
                company = input("Company name: ")
                position = input("Position: ")
                job_url = input("Job posting URL (optional): ")
                job_description = input("Paste job description (or press Enter to skip): ")
                location = input("Location: ")
        else:
            # Manual entry
            company = input("Company name: ")
            position = input("Position: ")
            job_url = input("Job posting URL (optional): ")
            job_description = input("Paste job description (or press Enter to skip): ")
            location = input("Location: ")
        
        # Additional details
        job_type = input("Job type (remote/hybrid/onsite): ")
        salary_range = input("Salary range (optional): ")
        
        print("\n⏳ Preparing your application materials...")
        
        # Check if we have AI capabilities
        if Config.OPENAI_API_KEY and job_description:
            print("🤖 Using AI to tailor your application...")
            tailored_resume = self.tailor.tailor_resume(job_description, company, position)
            cover_letter = self.tailor.generate_cover_letter(job_description, company, position)
        else:
            if not Config.OPENAI_API_KEY:
                print("⚠️ No AI key found. Using base resume and template cover letter.")
            else:
                print("⚠️ No job description provided. Using base resume.")
            tailored_resume = self.tailor.base_resume
            cover_letter = self.tailor.get_cover_letter_template(company, position)
        
        # Save to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        safe_position = "".join(c for c in position if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        
        resume_filename = f"data/resumes/{safe_company}_{safe_position}_{timestamp}_resume.txt"
        cover_filename = f"data/resumes/{safe_company}_{safe_position}_{timestamp}_cover.txt"
        
        os.makedirs('data/resumes', exist_ok=True)
        
        try:
            with open(resume_filename, 'w') as f:
                f.write(tailored_resume)
            
            with open(cover_filename, 'w') as f:
                f.write(cover_letter)
            
            print("\n✅ Documents generated successfully!")
            print(f"📄 Resume saved: {resume_filename}")
            print(f"📄 Cover letter saved: {cover_filename}")
        except Exception as e:
            print(f"Error saving files: {e}")
            return
        
        # Show preview
        print("\n--- COVER LETTER PREVIEW ---")
        preview_length = min(500, len(cover_letter))
        print(cover_letter[:preview_length])
        if len(cover_letter) > 500:
            print("...")
        
        # Log application
        app_id = self.db.add_application(
            company=company,
            position=position,
            job_url=job_url,
            resume=resume_filename,
            cover_letter=cover_filename,
            notes=f"Applied on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            salary_range=salary_range,
            location=location,
            job_type=job_type
        )
        
        print(f"\n🎉 Application logged! ID: {app_id}")
        
        # Set reminder
        print("\n📅 Don't forget to follow up in 1 week!")
        follow_up_date = datetime.now() + timedelta(days=7)
        print(f"   Suggested follow-up date: {follow_up_date.strftime('%Y-%m-%d')}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Review and polish the generated documents")
        print("2. Submit through the company's website")
        print("3. Update status to 'applied' in the tracker")
        print("4. Set a calendar reminder for follow-up")
        
        if job_url:
            print(f"\n🔗 Apply here: {job_url}")
            open_browser = input("\nOpen job posting in browser? (y/n): ")
            if open_browser.lower() == 'y':
                try:
                    import webbrowser
                    webbrowser.open(job_url)
                except Exception as e:
                    print(f"Couldn't open browser: {e}")
    
    def view_applications(self):
        """View and manage applications"""
        print("\n📊 YOUR APPLICATIONS")
        print("=" * 60)
        
        applications = self.db.get_applications(limit=50)
        
        if not applications:
            print("No applications yet! Start applying to track your progress.")
            return
        
        for app in applications:
            status_emoji = {
                'pending': '⏳',
                'applied': '📤',
                'interview': '🎤',
                'rejected': '❌',
                'offer': '🎉',
                'accepted': '✅'
            }.get(app['status'], '❓')
            
            print(f"\n{status_emoji} ID: {app['id']} | {app['position']} at {app['company']}")
            print(f"   📅 Applied: {app['date_applied'][:10] if app['date_applied'] else 'Unknown'}")
            print(f"   📍 Location: {app.get('location', 'Not specified')}")
            print(f"   💼 Type: {app.get('job_type', 'Not specified')}")
            print(f"   📊 Status: {app['status']}")
            
            if app.get('job_url'):
                print(f"   🔗 URL: {app['job_url'][:50]}...")
        
        # Option to update status
        print("\n" + "-"*60)
        update = input("\nUpdate application status? (y/n): ")
        if update.lower() == 'y':
            try:
                app_id = int(input("Enter application ID: "))
                print("\nStatus options:")
                print("  • pending (not yet submitted)")
                print("  • applied (application sent)")
                print("  • interview (got interview)")
                print("  • rejected (unfortunately rejected)")
                print("  • offer (received offer!)")
                print("  • accepted (offer accepted)")
                new_status = input("\nNew status: ").lower()
                self.db.update_status(app_id, new_status)
            except ValueError:
                print("Invalid input")
    
    def resume_management(self):
        """Manage resume"""
        while True:
            print("\n📄 RESUME MANAGEMENT")
            print("-" * 30)
            print("1. View current resume")
            print("2. Edit resume")
            print("3. Load resume from file")
            print("4. Save resume to file")
            print("5. Back to main menu")
            
            choice = input("\nChoose option (1-5): ").strip()
            
            if choice == '1':
                print("\n--- CURRENT RESUME ---")
                print(self.tailor.base_resume)
                
            elif choice == '2':
                print("\nPaste your updated resume (type 'END' on a new line when done):")
                lines = []
                while True:
                    try:
                        line = input()
                        if line.strip().upper() == 'END':
                            break
                        lines.append(line)
                    except KeyboardInterrupt:
                        print("\nCancelled")
                        break
                
                if lines:
                    resume_text = '\n'.join(lines)
                    self.tailor.save_resume(resume_text)
                
            elif choice == '3':
                filepath = input("Enter resume file path: ")
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            resume_text = f.read()
                        self.tailor.save_resume(resume_text)
                        print("✅ Resume loaded and saved!")
                    except Exception as e:
                        print(f"Error loading file: {e}")
                else:
                    print("❌ File not found!")
                    
            elif choice == '4':
                filepath = input("Enter path to save resume (e.g., my_resume.txt): ")
                try:
                    with open(filepath, 'w') as f:
                        f.write(self.tailor.base_resume)
                    print(f"✅ Resume saved to {filepath}")
                except Exception as e:
                    print(f"Error saving file: {e}")
                
            elif choice == '5':
                break
    
    def show_statistics(self):
        """Show application statistics"""
        stats = self.db.get_stats()
        
        print("\n📈 APPLICATION STATISTICS")
        print("=" * 60)
        print(f"📊 Total Applications: {stats['total']}")
        print(f"📅 Applications This Week: {stats['this_week']}")
        
        if stats['by_status']:
            print("\n📋 Applications by Status:")
            for status, count in stats['by_status']:
                emoji = {
                    'pending': '⏳',
                    'applied': '📤',
                    'interview': '🎤',
                    'rejected': '❌',
                    'offer': '🎉',
                    'accepted': '✅'
                }.get(status, '❓')
                print(f"   {emoji} {status.capitalize()}: {count}")
        
        # Calculate response rate
        if stats['total'] > 0:
            responses = sum(count for status, count in stats['by_status'] 
                          if status in ['interview', 'rejected', 'offer', 'accepted'])
            response_rate = (responses / stats['total']) * 100
            print(f"\n📬 Response Rate: {response_rate:.1f}%")
            
            # Interview conversion
            interviews = sum(count for status, count in stats['by_status'] 
                           if status in ['interview', 'offer', 'accepted'])
            if interviews > 0:
                interview_rate = (interviews / stats['total']) * 100
                print(f"🎤 Interview Rate: {interview_rate:.1f}%")
        
        print("\n💡 Insights & Tips:")
        if stats['total'] == 0:
            print("• Start applying! Track every application here.")
        elif stats['total'] < 10:
            print("• Keep going! Most people apply to 50+ jobs.")
        elif stats['this_week'] < 5:
            print("• Try to maintain 5-10 applications per week.")
        else:
            print("• Great pace! Keep the momentum going!")
        
        if stats['total'] > 20:
            print("• Remember to follow up on applications older than 1 week.")
            print("• Consider refining your resume if response rate is low.")
    
    def run(self):
        """Main application loop"""
        # Try to load existing resume
        if os.path.exists('data/base_resume.txt'):
            print("📄 Found saved resume")
        else:
            print("💡 Tip: Add your resume first (Option 4)")
        
        while True:
            try:
                choice = self.display_menu()
                
                if choice == '1':
                    self.job_search_menu()
                elif choice == '2':
                    self.apply_to_job()
                elif choice == '3':
                    self.view_applications()
                elif choice == '4':
                    self.resume_management()
                elif choice == '5':
                    self.show_statistics()
                elif choice == '6':
                    self.finder.search_tips()
                elif choice == '7':
                    print("\n👋 Good luck with your job search!")
                    print("💪 Remember: Every 'no' gets you closer to a 'yes'!")
                    print("🎯 Stay persistent and keep improving!\n")
                    break
                else:
                    print("❌ Invalid choice. Please try 1-7.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted. Returning to menu...")
                continue
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Returning to menu...")
                continue

if __name__ == "__main__":
    # Clear screen for better presentation
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                        ║
    ║        🎯 JOB APPLICATION ASSISTANT 🎯                ║
    ║           Your Smart Job Search Companion             ║
    ║                                                        ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Check for API key
    if not Config.OPENAI_API_KEY:
        print("    ⚠️  NOTE: Running without OpenAI API key")
        print("    AI features (smart resume tailoring) disabled")
        print("    Add key to .env to enable: OPENAI_API_KEY=sk-...")
        print()
        
        proceed = input("    Continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            print("\n    Exiting. Add your API key and try again!")
            sys.exit(0)
    else:
        print("    ✅ AI-Powered Resume Tailoring Enabled")
    
    print("\n    Starting application...\n")
    
    # Run the app
    app = JobApplicationAssistant()
    app.run()