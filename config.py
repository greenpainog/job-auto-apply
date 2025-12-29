import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database
    DATABASE_PATH = 'data/applications.db'
    
    # Folders
    RESUME_FOLDER = 'data/resumes'
    LOG_FOLDER = 'logs'
    DATA_FOLDER = 'data'
    
    # Create all necessary folders if they don't exist
    @classmethod
    def setup_folders(cls):
        """Create all required folders"""
        folders = [cls.DATA_FOLDER, cls.RESUME_FOLDER, cls.LOG_FOLDER]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Folder ready: {folder}")
    
    # Application Settings
    MAX_APPLICATIONS_PER_DAY = 10
    FOLLOW_UP_DAYS = 7
    
    # Resume Settings
    DEFAULT_RESUME_PATH = 'data/base_resume.txt'
    
    # Job Search Settings
    DEFAULT_LOCATION = 'Remote'
    DEFAULT_JOB_TYPE = 'Full-time'

# Run setup when module is imported
Config.setup_folders()

# Check if API key is configured
if Config.OPENAI_API_KEY:
    if Config.OPENAI_API_KEY.startswith('sk-'):
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key found but format looks incorrect")
else:
    print("⚠️  No OpenAI API key found - AI features will be limited")
    print("   Add to .env file: OPENAI_API_KEY=your-key-here")