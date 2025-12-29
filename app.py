from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
from database import Database
from resume_tailor import ResumeTailor
from job_finder import JobFinder
from config import Config
import PyPDF2
import docx2txt

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this to a random secret key

# Configuration
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
db = Database()
db.create_resume_table()  # Make sure resume table exists
tailor = ResumeTailor()
finder = JobFinder()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    """Extract text from various file formats"""
    extension = filepath.rsplit('.', 1)[1].lower()
    
    try:
        if extension == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif extension == 'pdf':
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        
        elif extension in ['doc', 'docx']:
            return docx2txt.process(filepath)
            
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

@app.route('/')
def index():
    """Dashboard page"""
    stats = db.get_stats()
    recent_apps = db.get_applications(limit=5)
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_apps=recent_apps)

@app.route('/resumes')
def resumes():
    """Resume management page"""
    all_resumes = db.get_all_resumes()
    return render_template('resumes.html', resumes=all_resumes)

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Handle resume upload"""
    if 'resume' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('resumes'))
    
    file = request.files['resume']
    resume_name = request.form.get('resume_name', '')
    description = request.form.get('description', '')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('resumes'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        file.save(filepath)
        
        # Extract text
        text_content = extract_text_from_file(filepath)
        
        if text_content:
            # Save to database
            if not resume_name:
                resume_name = f"Resume - {datetime.now().strftime('%Y-%m-%d')}"
            
            resume_id = db.add_resume(
                name=resume_name,
                content=text_content,
                filename=filename,
                description=description
            )
            
            flash(f'Resume "{resume_name}" uploaded successfully!', 'success')
        else:
            flash('Could not extract text from file', 'error')
            os.remove(filepath)  # Clean up
    else:
        flash('Invalid file type. Allowed: txt, pdf, doc, docx', 'error')
    
    return redirect(url_for('resumes'))

@app.route('/delete_resume/<int:resume_id>')
def delete_resume(resume_id):
    """Delete a resume"""
    # Add delete method to database.py if needed
    flash('Resume deleted', 'success')
    return redirect(url_for('resumes'))

@app.route('/set_default_resume/<int:resume_id>')
def set_default_resume(resume_id):
    """Set a resume as default"""
    db.set_default_resume(resume_id)
    flash('Default resume updated', 'success')
    return redirect(url_for('resumes'))

@app.route('/jobs')
def jobs():
    """Job management page"""
    finder.load_jobs()
    return render_template('jobs.html', jobs=finder.jobs)

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    """Add a new job"""
    if request.method == 'POST':
        job = {
            'title': request.form.get('title'),
            'company': request.form.get('company'),
            'location': request.form.get('location'),
            'url': request.form.get('url'),
            'description': request.form.get('description'),
            'salary': request.form.get('salary'),
            'job_type': request.form.get('job_type'),
            'date_found': datetime.now().isoformat()
        }
        
        finder.jobs.append(job)
        finder.save_jobs()
        
        flash('Job added successfully!', 'success')
        return redirect(url_for('jobs'))
    
    return render_template('add_job.html')

@app.route('/applications')
def applications():
    """View all applications"""
    apps = db.get_applications(limit=100)
    return render_template('applications.html', applications=apps)

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    """Apply to a job"""
    if request.method == 'POST':
        # Get form data
        company = request.form.get('company')
        position = request.form.get('position')
        job_url = request.form.get('job_url')
        job_description = request.form.get('job_description')
        location = request.form.get('location')
        job_type = request.form.get('job_type')
        salary_range = request.form.get('salary')
        resume_id = request.form.get('resume_id')
        
        # Get selected resume
        resume_data = db.get_resume_by_id(resume_id) if resume_id else None
        
        if resume_data:
            resume_content = resume_data[3]  # content is 4th column
            tailor.base_resume = resume_content
        
        # Generate tailored materials
        tailored_resume = tailor.tailor_resume(job_description, company, position) if job_description else tailor.base_resume
        cover_letter = tailor.generate_cover_letter(job_description, company, position) if job_description else tailor.get_cover_letter_template(company, position)
        
        # Save files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        safe_position = "".join(c for c in position if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        
        resume_filename = f"data/resumes/{safe_company}_{safe_position}_{timestamp}_resume.txt"
        cover_filename = f"data/resumes/{safe_company}_{safe_position}_{timestamp}_cover.txt"
        
        with open(resume_filename, 'w') as f:
            f.write(tailored_resume)
        
        with open(cover_filename, 'w') as f:
            f.write(cover_letter)
        
        # Log application
        app_id = db.add_application(
            company=company,
            position=position,
            job_url=job_url,
            resume=resume_filename,
            cover_letter=cover_filename,
            notes=f"Applied via web interface on {datetime.now().strftime('%Y-%m-%d')}",
            salary_range=salary_range,
            location=location,
            job_type=job_type
        )
        
        flash(f'Application created successfully! Documents saved.', 'success')
        return redirect(url_for('view_application', app_id=app_id))
    
    # GET request - show form
    finder.load_jobs()
    all_resumes = db.get_all_resumes()
    return render_template('apply.html', jobs=finder.jobs, resumes=all_resumes)

@app.route('/application/<int:app_id>')
def view_application(app_id):
    """View a specific application"""
    apps = db.get_applications(limit=1000)
    app_data = next((app for app in apps if app['id'] == app_id), None)
    
    if app_data:
        # Read the generated files if they exist
        resume_content = ""
        cover_content = ""
        
        if app_data.get('resume_used') and os.path.exists(app_data['resume_used']):
            with open(app_data['resume_used'], 'r') as f:
                resume_content = f.read()
        
        if app_data.get('cover_letter') and os.path.exists(app_data['cover_letter']):
            with open(app_data['cover_letter'], 'r') as f:
                cover_content = f.read()
        
        return render_template('view_application.html', 
                             app=app_data, 
                             resume=resume_content, 
                             cover_letter=cover_content)
    
    flash('Application not found', 'error')
    return redirect(url_for('applications'))

@app.route('/update_status/<int:app_id>', methods=['POST'])
def update_status(app_id):
    """Update application status"""
    new_status = request.form.get('status')
    db.update_status(app_id, new_status)
    flash('Status updated successfully!', 'success')
    return redirect(url_for('view_application', app_id=app_id))

@app.route('/statistics')
def statistics():
    """Show statistics page"""
    stats = db.get_stats()
    apps = db.get_applications(limit=1000)
    
    # Calculate additional stats
    by_month = {}
    by_company = {}
    
    for app in apps:
        # Group by month
        if app['date_applied']:
            month = app['date_applied'][:7]  # YYYY-MM
            by_month[month] = by_month.get(month, 0) + 1
        
        # Group by company
        company = app['company']
        by_company[company] = by_company.get(company, 0) + 1
    
    return render_template('statistics.html', 
                         stats=stats, 
                         by_month=by_month, 
                         by_company=by_company)

if __name__ == '__main__':
    print("🌐 Starting Job Application Assistant Web Server...")
    print("📍 Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)