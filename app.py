from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import requests
import json
import re
import random
import string
import hashlib
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dracin-viewer-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dracin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dracinviewer@gmail.com'
app.config['MAIL_PASSWORD'] = 'upiu svef mpab owqo'

db = SQLAlchemy(app)
mail = Mail(app)

# Konfigurasi Dracin Viewer
APP_NAME = "Dracin Viewer"
APP_TAGLINE = "Platform Nonton Drama China Terbaik"
COPYRIGHT_NAME = "AmmarBN"
COPYRIGHT_URL = "https://github.com/AmmarrBN"

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def __init__(self, email, code):
        self.email = email
        self.code = code
        self.expires_at = datetime.utcnow() + timedelta(minutes=10)

class WatchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String(100), nullable=False)
    book_title = db.Column(db.String(200))
    episode_num = db.Column(db.Integer)
    watched_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

class ReelShortAPI:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.reelshort.com/",
            "Origin": "https://www.reelshort.com"
        }
        self.base_url = "https://www.reelshort.com/_next/data/acf624d/id"
    
    def search(self, keywords):
        encoded_keywords = keywords.replace(" ", "+")
        url = f"{self.base_url}/search.json?keywords={encoded_keywords}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            books = data.get("pageProps", {}).get("books", [])
            results = []
            
            for book in books:
                filtered_title = self._filter_title(book.get("book_title", ""))
                
                results.append({
                    "book_title": book.get("book_title"),
                    "filtered_title": filtered_title,
                    "book_pic": book.get("book_pic"),
                    "special_desc": book.get("special_desc"),
                    "tag": book.get("tag", []),
                    "_id": book.get("_id"),
                    "chapter_count": book.get("chapter_count", 0),
                    "read_count": book.get("read_count", 0)
                })
            return results
        except Exception as e:
            print(f"Error search: {e}")
            return []
    
    def get_episodes(self, book_id, filtered_title):
        url = f"{self.base_url}/movie/{filtered_title}-{book_id}.json?slug={filtered_title}-{book_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            book_data = data.get("pageProps", {}).get("data", {})
            episodes = book_data.get("online_base", [])
            
            results = []
            for ep in episodes:
                results.append({
                    "episode": ep.get("serial_number"),
                    "chapter_id": ep.get("chapter_id")
                })
            return results
        except Exception as e:
            print(f"Error get episodes: {e}")
            return []
    
    def get_video_url(self, episode_num, filtered_title, book_id, chapter_id):
        url = f"{self.base_url}/episodes/episode-{episode_num}-{filtered_title}-{book_id}-{chapter_id}.json?play_time=1&slug=episode-{episode_num}-{filtered_title}-{book_id}-{chapter_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            episode_data = data.get("pageProps", {}).get("data", {})
            
            return {
                "video_url": episode_data.get("video_url", ""),
                "book_title": episode_data.get("book_title", ""),
                "chapter_desc": episode_data.get("chapter_desc", ""),
                "duration": episode_data.get("duration", 0),
                "video_pic": episode_data.get("video_pic", ""),
                "serial_number": episode_data.get("serial_number", 0),
                "chapter_count": episode_data.get("chapter_count", 0)
            }
        except Exception as e:
            print(f"Error get video: {e}")
            return None
    
    def _filter_title(self, title):
        filtered = title.lower()
        filtered = re.sub(r'[^a-z0-9]+', ' ', filtered)
        filtered = re.sub(r'\s+', ' ', filtered).strip()
        filtered = filtered.replace(' ', '-')
        return filtered

api = ReelShortAPI()

# Captcha Generator
def generate_captcha():
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    operator = random.choice(['+', '-', 'x'])
    
    if operator == '+':
        answer = num1 + num2
    elif operator == '-':
        answer = num1 - num2
    else:
        answer = num1 * num2
    
    question = f"{num1} {operator} {num2} = ?"
    return question, str(answer)

def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

# Context Processor
@app.context_processor
def inject_globals():
    return dict(
        app_name=APP_NAME,
        app_tagline=APP_TAGLINE,
        copyright_name=COPYRIGHT_NAME,
        copyright_url=COPYRIGHT_URL,
        current_user=session.get('user_id')
    )

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search():
    keywords = request.form.get('keywords', '')
    if not keywords:
        return jsonify({'error': 'Keywords required'}), 400
    
    results = api.search(keywords)
    return jsonify({'results': results})

@app.route('/episodes/<book_id>')
def episodes(book_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu', 'warning')
        return redirect(url_for('login'))
    
    filtered_title = request.args.get('filtered_title', '')
    book_title = request.args.get('book_title', '')
    book_pic = request.args.get('book_pic', '')
    
    episodes_list = api.get_episodes(book_id, filtered_title)
    
    return render_template('episodes.html', 
                         book_id=book_id,
                         filtered_title=filtered_title,
                         book_title=book_title,
                         book_pic=book_pic,
                         episodes=episodes_list)

@app.route('/watch/<book_id>/<int:episode_num>')
def watch(book_id, episode_num):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu', 'warning')
        return redirect(url_for('login'))
    
    filtered_title = request.args.get('filtered_title', '')
    chapter_id = request.args.get('chapter_id', '')
    book_title = request.args.get('book_title', '')
    
    video_data = api.get_video_url(episode_num, filtered_title, book_id, chapter_id)
    
    if not video_data or not video_data.get('video_url'):
        return "Video not found", 404
    
    episodes_list = api.get_episodes(book_id, filtered_title)
    
    next_episode = None
    for i, ep in enumerate(episodes_list):
        if ep['episode'] == episode_num and i + 1 < len(episodes_list):
            next_episode = episodes_list[i + 1]
            break
    
    return render_template('watch.html',
                         book_id=book_id,
                         filtered_title=filtered_title,
                         book_title=book_title,
                         episode_num=episode_num,
                         chapter_id=chapter_id,
                         video_url=video_data['video_url'],
                         video_pic=video_data['video_pic'],
                         duration=video_data['duration'],
                         chapter_desc=video_data['chapter_desc'],
                         next_episode=next_episode,
                         total_episodes=video_data['chapter_count'])

@app.route('/api/episodes/<book_id>')
def api_episodes(book_id):
    filtered_title = request.args.get('filtered_title', '')
    episodes = api.get_episodes(book_id, filtered_title)
    return jsonify({'episodes': episodes})

@app.route('/api/video/<book_id>/<int:episode_num>')
def api_video(book_id, episode_num):
    filtered_title = request.args.get('filtered_title', '')
    chapter_id = request.args.get('chapter_id', '')
    
    video_data = api.get_video_url(episode_num, filtered_title, book_id, chapter_id)
    
    if not video_data:
        return jsonify({'error': 'Video not found'}), 404
    
    episodes_list = api.get_episodes(book_id, filtered_title)
    next_episode = None
    
    for i, ep in enumerate(episodes_list):
        if ep['episode'] == episode_num and i + 1 < len(episodes_list):
            next_episode = {
                'episode': episodes_list[i + 1]['episode'],
                'chapter_id': episodes_list[i + 1]['chapter_id']
            }
            break
    
    return jsonify({
        'video_url': video_data['video_url'],
        'episode': video_data['serial_number'],
        'duration': video_data['duration'],
        'next_episode': next_episode
    })

# Auth Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        step = request.form.get('step', '1')
        
        if step == '1':
            # Step 1: Validate captcha and send email
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            captcha_answer = request.form.get('captcha_answer', '')
            captcha_session = session.get('captcha_answer', '')
            
            # Validations
            if not all([username, email, password]):
                flash('Semua field harus diisi', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Password minimal 6 karakter', 'error')
                return redirect(url_for('register'))
            
            if captcha_answer != captcha_session:
                flash('Captcha salah, coba lagi', 'error')
                return redirect(url_for('register'))
            
            # Check existing user
            if User.query.filter_by(username=username).first():
                flash('Username sudah digunakan', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email sudah terdaftar', 'error')
                return redirect(url_for('register'))
            
            # Generate and send verification code
            code = generate_verification_code()
            verif = VerificationCode(email=email, code=code)
            db.session.add(verif)
            db.session.commit()
            
            # Send email
            try:
                msg = Message('Kode Verifikasi Dracin Viewer', 
                            sender=app.config['MAIL_USERNAME'],
                            recipients=[email])
                msg.body = f'''Halo {username},

Terima kasih telah mendaftar di Dracin Viewer!

Kode verifikasi Anda: {code}

Kode ini berlaku selama 10 menit.

Jika Anda tidak mendaftar, abaikan email ini.

Salam,
Dracin Viewer Team'''
                mail.send(msg)
                
                # Store temp data in session
                session['temp_username'] = username
                session['temp_email'] = email
                session['temp_password'] = password
                
                flash('Kode verifikasi telah dikirim ke email Anda', 'success')
                return render_template('verify_email.html', email=email)
                
            except Exception as e:
                print(f"Email error: {e}")
                flash('Gagal mengirim email, coba lagi nanti', 'error')
                return redirect(url_for('register'))
        
        elif step == '2':
            # Step 2: Verify code
            code = request.form.get('verification_code', '')
            email = session.get('temp_email', '')
            
            if not email:
                flash('Sesi habis, silakan daftar ulang', 'error')
                return redirect(url_for('register'))
            
            # Check code
            verif = VerificationCode.query.filter_by(email=email, code=code).first()
            
            if not verif or verif.expires_at < datetime.utcnow():
                flash('Kode verifikasi salah atau sudah kadaluarsa', 'error')
                return render_template('verify_email.html', email=email)
            
            # Create user
            user = User(
                username=session['temp_username'],
                email=email
            )
            user.set_password(session['temp_password'])
            
            db.session.add(user)
            db.session.delete(verif)
            db.session.commit()
            
            # Clear temp session
            session.pop('temp_username', None)
            session.pop('temp_email', None)
            session.pop('temp_password', None)
            
            flash('Registrasi berhasil! Silakan login', 'success')
            return redirect(url_for('login'))
    
    # GET request - generate new captcha
    captcha_q, captcha_a = generate_captcha()
    session['captcha_answer'] = captcha_a
    
    return render_template('register.html', captcha_question=captcha_q)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Check by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username/Email atau password salah', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    history = WatchHistory.query.filter_by(user_id=user.id).order_by(WatchHistory.watched_at.desc()).limit(10).all()
    
    return render_template('profile.html', user=user, history=history)

@app.route('/resend-code', methods=['POST'])
def resend_code():
    email = session.get('temp_email', '')
    if not email:
        return jsonify({'error': 'Sesi habis'}), 400
    
    # Generate new code
    code = generate_verification_code()
    
    # Delete old codes
    VerificationCode.query.filter_by(email=email).delete()
    
    # Create new code
    verif = VerificationCode(email=email, code=code)
    db.session.add(verif)
    db.session.commit()
    
    # Send email
    try:
        msg = Message('Kode Verifikasi Dracin Viewer (Resend)', 
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[email])
        msg.body = f'''Kode verifikasi baru Anda: {code}

Kode ini berlaku selama 10 menit.'''
        mail.send(msg)
        
        return jsonify({'success': True, 'message': 'Kode baru telah dikirim'})
    except Exception as e:
        return jsonify({'error': 'Gagal mengirim email'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
