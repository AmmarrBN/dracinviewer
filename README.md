# 🎬 Dracin Viewer

<p align="center">
  <img src="https://img.shields.io/badge/Flask-3.0.0-black?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11.6-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<p align="center">
  <b>Platform Streaming Drama China Gratis</b><br>
  Tonton Drama Cina Secara Gratis Di Dracin Viewer
</p>

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 🔍 **Pencarian Cepat** | Cari ribuan drama China secara instan |
| 📺 **Streaming HD** | Kualitas video tinggi dengan minimal buffering |
| ⏭️ **Auto Next Episode** | Marathon tanpa henti, lanjut otomatis ke episode berikutnya |
| 📱 **Responsive Design** | Optimal di desktop, tablet, dan mobile |
| 🔐 **Autentikasi** | Sistem login dengan verifikasi email |
| 📚 **Riwayat Tontonan** | Masih Error |

---

## 🛠️ Tech Stack

- **Backend:** Flask 3.0.0 + SQLAlchemy
- **Database:** PostgreSQL (Production) / SQLite (Development)
- **Frontend:** HTML + CSS + JavaScript
- **Deployment:** Heroku + Gunicorn
- **Email Service:** Gmail SMTP
- **Video Player:** HLS.js untuk streaming HLS

---

## 📡 Data Source

> ⚠️ **Disclaimer:** Aplikasi ini menggunakan **unofficial API** dari [ReelShort](https://www.reelshort.com) untuk mengambil data drama dan video. 

**Teknik yang digunakan:**
- **API Sniffing/Scraping** dari endpoint ReelShort
- **Reverse Engineering** terhadap API internal ReelShort
- **Dynamic Routing** untuk mengakses episode dan video URL

**Endpoint yang diakses:**
```python
https://www.reelshort.com/_next/data/acf624d/id/search.json
https://www.reelshort.com/_next/data/acf624d/id/movie/{title}-{id}.json
https://www.reelshort.com/_next/data/acf624d/id/episodes/episode-{num}-{title}-{id}-{chapter}.json
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git
- Heroku CLI (untuk deployment)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/username/dracin-viewer.git
cd dracin-viewer

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Setup environment variables
# Buat file .env di root folder, isi:
# SECRET_KEY=your-secret-key
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password

# 6. Jalankan aplikasi
python app.py
```

Akses di `http://localhost:5000`

---

## 🌐 Deployment Heroku

```bash
# 1. Login Heroku
heroku login

# 2. Buat aplikasi
heroku create nama-aplikasi-lu

# 3. Tambahkan PostgreSQL
heroku addons:create heroku-postgresql:mini

# 4. Set environment variables
heroku config:set SECRET_KEY="$(openssl rand -base64 32)"
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password

# 5. Deploy
git push heroku main

# 6. Buka aplikasi
heroku open
```

---

## 🔧 Environment Variables

| Variable | Deskripsi | Wajib |
|----------|-----------|-------|
| `SECRET_KEY` | Kunci enkripsi session | ✅ |
| `DATABASE_URL` | URL database PostgreSQL | ✅ (Heroku otomatis) |
| `MAIL_USERNAME` | Email Gmail untuk verifikasi | ✅ |
| `MAIL_PASSWORD` | App Password Gmail | ✅ |
| `MAIL_SERVER` | SMTP server (default: smtp.gmail.com) | ❌ |
| `MAIL_PORT` | Port SMTP (default: 587) | ❌ |
| `MAIL_USE_TLS` | Enable TLS (default: True) | ❌ |

---

## 📁 Project Structure

```
dracinviewer/
├── app.py                 # Main application & API handlers
├── config.py              # Configuration classes
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku process configuration
├── runtime.txt           # Python version specification
├── README.md             # This file
├── templates/            # HTML Templates (Jinja2)
│   ├── base.html         # Base layout
│   ├── index.html        # Homepage & search
│   ├── login.html        # Login page
│   ├── register.html     # Registration
│   ├── verify_email.html # Email verification
│   ├── profile.html      # User profile
│   ├── episodes.html     # Episode list
│   ├── watch.html        # Video player
│   ├── about.html        # About page
│   └── faq.html          # FAQ page
└── static/               # Static assets (CSS, JS, images)
```

---

## 🎯 API Endpoints

| Endpoint | Method | Deskripsi |
|----------|--------|-----------|
| `/` | GET | Homepage |
| `/search` | POST | Cari drama |
| `/episodes/<book_id>` | GET | Daftar episode |
| `/watch/<book_id>/<ep>` | GET | Halaman nonton |
| `/api/episodes/<book_id>` | GET | API daftar episode (JSON) |
| `/api/video/<book_id>/<ep>` | GET | API video URL (JSON) |
| `/register` | GET/POST | Registrasi user |
| `/login` | GET/POST | Login user |
| `/logout` | GET | Logout |
| `/profile` | GET | Profil user |
| `/resend-code` | POST | Kirim ulang kode verifikasi |

---

---

## For Your Information

> **Aplikasi ini dibuat untuk tujuan menonton video Drama secara gratis**

- **Data Source:** Menggunakan unofficial API dari ReelShort
- **Copyright:** Semua konten video milik ReelShort dan pemilik sah
- **Usage:** Gunakan dengan bijak dan bertanggung jawab
- **Liability:** Developer tidak bertanggung jawab atas penyalahgunaan

---

## 🤝 Contributing
1. Fork repository
2. New Branch
3. Commit repo
4. Push Branch
5. Pull Request

---

## 📝 License

Distributed under the MIT License.

---

## 👨‍💻 Author

**AmmarBN**

- GitHub: [@AmmarrBN](https://github.com/AmmarrBN)

---

<p align="center">
  Made with ❤️ in Indonesia
</p>
