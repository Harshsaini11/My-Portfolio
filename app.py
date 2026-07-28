import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)

# File Upload Configuration (PDF Support Added)
UPLOAD_FOLDER = os.path.join('static', 'assets')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

DATABASE = 'portfolio.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. CMS Content Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            key_name TEXT PRIMARY KEY,
            content_value TEXT NOT NULL
        )
    ''')

    # 2. Projects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            tech_stack TEXT NOT NULL,
            image_url TEXT NOT NULL,
            github_url TEXT NOT NULL,
            demo_url TEXT
        )
    ''')

    # 3. Internships Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            company TEXT NOT NULL,
            duration TEXT NOT NULL,
            description TEXT NOT NULL,
            technologies TEXT NOT NULL,
            certificate_link TEXT,
            offer_letter_link TEXT
        )
    ''')

    # 4. Admin Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 5. Experience Table Update
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon TEXT NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            description TEXT,
            points TEXT,
            tag TEXT
        )
    ''')
    
    # 6. Services Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            icon TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    
    cursor.execute('SELECT * FROM admin WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute('INSERT INTO admin (username, password_hash) VALUES (?, ?)', ('admin', hashed_pw))
    
    conn.commit()
    conn.close()

init_db()


# --- Routes ---
@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT content_value FROM content WHERE key_name = ?', ('hero_profile_img',))
    row = cursor.fetchone()
    conn.close()
    
    profile_img = row['content_value'] if row else '/static/assets/profile.jpg'
    return render_template('index.html', is_admin=False, profile_img=profile_img)

@app.route('/admin')
def admin_page():
    if not session.get('is_admin'):
        return render_template('admin_login.html')
    return render_template('index.html', is_admin=True)

# Temporary OTP Store (In-Memory)
otp_store = {}

# 1. Update Password API (When Admin is Logged In)
@app.route('/api/admin/update-password', methods=['POST'])
def update_password():
    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized', 'message': 'Admin login required'}), 401
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE username = ?', ('admin',))
    admin = cursor.fetchone()
    
    if admin and check_password_hash(admin['password_hash'], current_password):
        new_hashed_pw = generate_password_hash(new_password)
        cursor.execute('UPDATE admin SET password_hash = ? WHERE username = ?', (new_hashed_pw, 'admin'))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Password updated successfully!'})
    
    conn.close()
    return jsonify({'status': 'error', 'message': 'Incorrect current password'}), 400

# 2. Send Reset OTP API (Forgot Password)
@app.route('/api/admin/forgot-password', methods=['POST'])
def forgot_password():
    # 6-digit OTP generate karein
    otp = str(random.randint(100000, 999999))
    otp_store['admin_otp'] = otp
    
    msg = Message(
        subject="Admin Password Reset OTP - Portfolio",
        sender=app.config['MAIL_USERNAME'],
        recipients=['Harshsaini2452005@gmail.com']
    )
    msg.body = f"Your Password Reset OTP is: {otp}\n\nIf you did not request this, please ignore."
    
    try:
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'OTP sent to registered email!'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'Failed to send OTP email.'}), 500

# 3. Verify OTP & Reset Password API
@app.route('/api/admin/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    entered_otp = data.get('otp')
    new_password = data.get('new_password')
    
    if otp_store.get('admin_otp') and otp_store['admin_otp'] == entered_otp:
        new_hashed_pw = generate_password_hash(new_password)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE admin SET password_hash = ? WHERE username = ?', (new_hashed_pw, 'admin'))
        conn.commit()
        conn.close()
        
        # OTP clear karein reset hone ke baad
        otp_store.pop('admin_otp', None)
        return jsonify({'status': 'success', 'message': 'Password reset successfully! You can now login.'})
    
    return jsonify({'status': 'error', 'message': 'Invalid or expired OTP'}), 400

# --- Auth APIs ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE username = ?', (data.get('username'),))
    admin = cursor.fetchone()
    conn.close()
    
    if admin and check_password_hash(admin['password_hash'], data.get('password')):
        session['is_admin'] = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid Username or Password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return jsonify({'status': 'success'})

# --- File Upload API ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if not session.get('is_admin'):
            return jsonify({'status': 'unauthorized', 'message': 'Admin login required'}), 401
        
        file_key = 'file' if 'file' in request.files else ('image' if 'image' in request.files else None)
        if not file_key:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
        
        file = request.files[file_key]
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
            
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()
            base_name = os.path.splitext(filename)[0]
            unique_filename = f"{base_name}_{os.urandom(4).hex()}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            return jsonify({'status': 'success', 'file_url': f"/static/assets/{unique_filename}"})
        
        return jsonify({'status': 'error', 'message': 'Invalid file format'}), 400
    except Exception as e:
        print("Upload Server Exception:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Dynamic Content APIs ---
@app.route('/api/content', methods=['GET'])
def get_content():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content')
    rows = cursor.fetchall()
    conn.close()
    content = {row['key_name']: row['content_value'] for row in rows}
    return jsonify(content)

@app.route('/api/content/save', methods=['POST'])
def save_content():
    try:
        if not session.get('is_admin'):
            return jsonify({'status': 'unauthorized', 'message': 'Admin login required'}), 401
        
        data = request.json or {}
        conn = get_db()
        cursor = conn.cursor()
        for key, value in data.items():
            cursor.execute('''
                INSERT INTO content (key_name, content_value)
                VALUES (?, ?)
                ON CONFLICT(key_name) DO UPDATE SET content_value=excluded.content_value
            ''', (key, value))
            
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'All changes saved live!'})
    except Exception as e:
        print("Save Content Exception:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def sanitize_image_url(url_str):
    if not url_str:
        return '/static/assets/default-project.png'
    
    url_str = url_str.strip()
    if 'static' in url_str:
        static_index = url_str.find('static')
        cleaned_path = url_str[static_index:].replace('\\', '/')
        return '/' + cleaned_path
        
    if url_str.startswith(('http://', 'https://', '//', '/')):
        return url_str
        
    return url_str

# --- Projects APIs ---
@app.route('/api/projects', methods=['GET', 'POST'])
def manage_projects():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM projects ORDER BY id DESC')
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(projects)

    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401

    data = request.json
    tech_stack_str = ','.join(data['tech_stack']) if isinstance(data['tech_stack'], list) else data.get('tech_stack', '')
    clean_image_url = sanitize_image_url(data.get('image_url', ''))

    cursor.execute('''
        INSERT INTO projects (title, description, tech_stack, image_url, github_url, demo_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.get('title'), data.get('description'), tech_stack_str, clean_image_url, data.get('github_url'), data.get('demo_url', '#')))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/projects/<int:project_id>', methods=['PUT', 'DELETE'])
def update_or_delete_project(project_id):
    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'DELETE':
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    elif request.method == 'PUT':
        data = request.json
        tech_stack_str = ','.join(data['tech_stack']) if isinstance(data['tech_stack'], list) else data.get('tech_stack', '')
        clean_image_url = sanitize_image_url(data.get('image_url', ''))

        cursor.execute('''
            UPDATE projects 
            SET title = ?, description = ?, tech_stack = ?, image_url = ?, github_url = ?, demo_url = ?
            WHERE id = ?
        ''', (data.get('title'), data.get('description'), tech_stack_str, clean_image_url, data.get('github_url'), data.get('demo_url', '#'), project_id))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# --- Internships APIs ---
@app.route('/api/internships', methods=['GET', 'POST'])
def manage_internships():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM internships ORDER BY id DESC')
        internships = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(internships)

    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401

    data = request.json
    tech_str = ','.join(data['technologies']) if isinstance(data['technologies'], list) else data['technologies']
    cursor.execute('''
        INSERT INTO internships (role, company, duration, description, technologies, certificate_link, offer_letter_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['role'], 
        data['company'], 
        data['duration'], 
        data['description'], 
        tech_str, 
        data.get('certificate_link', '#'),
        data.get('offer_letter_link', '#')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/internships/<int:intern_id>', methods=['PUT', 'DELETE'])
def update_or_delete_internship(intern_id):
    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'DELETE':
        cursor.execute('DELETE FROM internships WHERE id = ?', (intern_id,))
    elif request.method == 'PUT':
        data = request.json
        tech_str = ','.join(data['technologies']) if isinstance(data['technologies'], list) else data['technologies']
        cursor.execute('''
            UPDATE internships 
            SET role = ?, company = ?, duration = ?, description = ?, technologies = ?, certificate_link = ?, offer_letter_link = ?
            WHERE id = ?
        ''', (
            data['role'], 
            data['company'], 
            data['duration'], 
            data['description'], 
            tech_str, 
            data.get('certificate_link', '#'),
            data.get('offer_letter_link', '#'),
            intern_id
        ))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# --- Experience APIs ---
@app.route('/api/experience', methods=['GET', 'POST'])
def manage_experience():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM experience ORDER BY id ASC')
        exp_list = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(exp_list)

    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401

    data = request.json
    cursor.execute('''
        INSERT INTO experience (icon, title, subtitle, description, points, tag)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get('icon', 'fa-briefcase'), 
        data.get('title'), 
        data.get('subtitle', ''), 
        data.get('description', ''), 
        data.get('points', ''), 
        data.get('tag', '')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/experience/<int:exp_id>', methods=['PUT', 'DELETE'])
def update_or_delete_experience(exp_id):
    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'DELETE':
        cursor.execute('DELETE FROM experience WHERE id = ?', (exp_id,))
    elif request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE experience 
            SET icon = ?, title = ?, subtitle = ?, description = ?, points = ?, tag = ?
            WHERE id = ?
        ''', (
            data.get('icon', 'fa-briefcase'), 
            data.get('title'), 
            data.get('subtitle', ''), 
            data.get('description', ''), 
            data.get('points', ''), 
            data.get('tag', ''),
            exp_id
        ))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# --- Services APIs ---
@app.route('/api/services', methods=['GET', 'POST'])
def manage_services():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM services ORDER BY id ASC')
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(services)

    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401

    data = request.json
    cursor.execute('''
        INSERT INTO services (icon, title, description)
        VALUES (?, ?, ?)
    ''', (
        data.get('icon', 'fa-code'), 
        data.get('title'), 
        data.get('description')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/services/<int:service_id>', methods=['PUT', 'DELETE'])
def update_or_delete_service(service_id):
    if not session.get('is_admin'):
        return jsonify({'status': 'unauthorized'}), 401
    
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'DELETE':
        cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    elif request.method == 'PUT':
        data = request.json
        cursor.execute('''
            UPDATE services 
            SET icon = ?, title = ?, description = ?
            WHERE id = ?
        ''', (
            data.get('icon', 'fa-code'), 
            data.get('title'), 
            data.get('description'),
            service_id
        ))
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'Harshsaini2452005@gmail.com'
app.config['MAIL_PASSWORD'] = 'mlkxrewpepqxccpo'

mail = Mail(app)

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')

    msg = Message(
        subject=f"Portfolio Contact: {subject}",
        sender=app.config['MAIL_USERNAME'],
        recipients=['Harshsaini2452005@gmail.com']
    )
    msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    try:
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Email sent successfully!'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'Failed to send email.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)