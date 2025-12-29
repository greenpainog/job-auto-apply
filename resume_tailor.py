import openai
from config import Config
import json
import os
from datetime import datetime

class ResumeTailor:
    def __init__(self):
        if Config.OPENAI_API_KEY:
            # Try new OpenAI client format first (v1.0+)
            try:
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                self.use_new_api = True
                print("✅ OpenAI API configured (new version)")
            except AttributeError:
                # Fall back to old format (v0.28)
                openai.api_key = Config.OPENAI_API_KEY
                self.client = None
                self.use_new_api = False
                print("✅ OpenAI API configured (legacy version)")
        else:
            print("⚠️ No OpenAI API key found. AI features disabled.")
            self.client = None
            self.use_new_api = False
        
        self.base_resume = None
        self.load_default_resume()
    
    def load_default_resume(self):
        """Load default resume from file if exists"""
        default_path = 'data/base_resume.txt'
        if os.path.exists(default_path):
            with open(default_path, 'r') as f:
                self.base_resume = f.read()
                print("✅ Loaded saved resume")
        else:
            # Default template
            self.base_resume = """
[Your Name]
[Email] | [Phone] | [LinkedIn] | [GitHub]

PROFESSIONAL SUMMARY
Experienced professional seeking new opportunities to contribute my skills and grow.

SKILLS
• Programming: Python, JavaScript, SQL
• Tools: Git, VS Code, Linux
• Soft Skills: Problem-solving, Communication, Team collaboration

EXPERIENCE
[Add your work experience here]
• Company Name | Position | Dates
  - Achievement/Responsibility 1
  - Achievement/Responsibility 2

EDUCATION
[Add your education here]
• Degree, University, Year

PROJECTS
[Add relevant projects here]
• Project Name: Brief description and technologies used
"""
    
    def save_resume(self, resume_text=None):
        """Save resume to file"""
        if resume_text:
            self.base_resume = resume_text
        
        with open('data/base_resume.txt', 'w') as f:
            f.write(self.base_resume)
        print("✅ Resume saved to data/base_resume.txt")
    
    def _call_openai_api(self, messages, temperature=0.7, max_tokens=1500):
        """Helper method to call OpenAI API with version handling"""
        try:
            if self.use_new_api and self.client:
                # New API format (v1.0+)
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            else:
                # Old API format (v0.28)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"❌ OpenAI API Error: {e}")
            return None
    
    def tailor_resume(self, job_description, company_name=None, position=None):
        """Customize resume for specific job using AI"""
        if not Config.OPENAI_API_KEY:
            print("⚠️ AI features not available. Returning base resume.")
            return self.base_resume
        
        if not self.base_resume:
            print("❌ No base resume loaded!")
            return None
        
        prompt = f"""
        Please tailor this resume for the following job. 
        Make it ATS-friendly and highlight relevant skills.
        Keep all the actual information but optimize keywords and phrasing.
        Do not make up any new experience or skills not in the original.
        
        Company: {company_name if company_name else 'Tech Company'}
        Position: {position if position else 'Not specified'}
        
        Job Description:
        {job_description[:2000]}  # Limit to avoid token limits
        
        Current Resume:
        {self.base_resume}
        
        Return ONLY the tailored resume in a clean format, no explanations.
        """
        
        messages = [
            {"role": "system", "content": "You are a professional resume writer. Keep all factual information unchanged."},
            {"role": "user", "content": prompt}
        ]
        
        print("🤖 Tailoring resume with AI...")
        result = self._call_openai_api(messages, temperature=0.7, max_tokens=1500)
        
        if result:
            return result
        else:
            print("⚠️ Failed to tailor resume, using base version")
            return self.base_resume
    
    def generate_cover_letter(self, job_description, company_name, position):
        """Generate a cover letter using AI"""
        if not Config.OPENAI_API_KEY:
            print("⚠️ AI features not available.")
            return self.get_cover_letter_template(company_name, position)
        
        if not self.base_resume:
            print("❌ No base resume loaded!")
            return None
        
        prompt = f"""
        Write a concise, professional cover letter for this position.
        Make it genuine, specific to the role, and about 250-300 words.
        
        Position: {position}
        Company: {company_name}
        
        Job Description:
        {job_description[:1500]}
        
        Base it on this resume:
        {self.base_resume}
        
        Format:
        - Professional greeting
        - Strong opening paragraph showing enthusiasm
        - 1-2 paragraphs highlighting relevant experience
        - Closing paragraph with call to action
        - Professional sign-off
        
        Return ONLY the cover letter text, no explanations.
        """
        
        messages = [
            {"role": "system", "content": "You are a professional cover letter writer."},
            {"role": "user", "content": prompt}
        ]
        
        print("🤖 Generating cover letter with AI...")
        result = self._call_openai_api(messages, temperature=0.8, max_tokens=800)
        
        if result:
            return result
        else:
            print("⚠️ Failed to generate AI cover letter, using template")
            return self.get_cover_letter_template(company_name, position)
    
    def get_cover_letter_template(self, company_name, position):
        """Fallback template if AI is not available"""
        return f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company_name}. 
With my experience and passion for technology, I am confident I would be a valuable addition to your team.

[Add specific reasons why you're interested in this company]

[Highlight 2-3 relevant experiences or skills from your resume]

[Mention a specific achievement or project relevant to this role]

I am excited about the opportunity to contribute to {company_name} and would welcome the chance 
to discuss how my skills and experience align with your needs.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
[Your Name]
"""
    
    def extract_keywords(self, job_description):
        """Extract key skills and requirements from job description"""
        # Simple keyword extraction without AI
        keywords = []
        tech_keywords = ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 
                       'kubernetes', 'react', 'node', 'git', 'agile', 'scrum',
                       'typescript', 'mongodb', 'postgresql', 'redis', 'flask',
                       'django', 'fastapi', 'machine learning', 'data science']
        
        job_lower = job_description.lower()
        for keyword in tech_keywords:
            if keyword in job_lower:
                keywords.append(keyword)
        
        return keywords