# CyberEye 🛡️

**Smart cybersecurity detection at your fingertips.**
CyberEye is a full-stack web application that scans URLs and phone numbers in
real time to detect phishing, fraud, and malicious content — before users
click, call, or share. Built as a multi-layered detection pipeline that
combines local heuristics with trusted third-party threat intelligence.

---

## ✨ Features

- 🔗 **URL scanning** — heuristic analysis + Google Safe Browsing + VirusTotal
- 📞 **Phone scanning** — E.164 normalization, local pattern detection, and external phone-info lookup
- 👤 **User accounts** — sign up, email-OTP verification, JWT-protected sessions
- 🧠 **Profiles** — display name, bio, avatar, and per-user scan stats
- 🕓 **Scan history** — paginated, filterable, deletable history per user
- 🌍 **Country list** — endpoint that returns all countries with their phone codes
- 🟢 **Verdicts** — every scan returns one of: `safe` · `suspicious` · `phishing` · `unknown`

---

## 🧱 Tech Stack

| Layer           | Technology                                                  |
|-----------------|-------------------------------------------------------------|
| Frontend        | HTML, CSS, JavaScript (vanilla)                             |
| Backend         | Python 3.11+, FastAPI, Uvicorn                              |
| Database        | SQLite (via SQLAlchemy ORM)                                 |
| Auth            | bcrypt (password hashing), python-jose (JWT)                |
| Email / OTP     | Python `smtplib` over Gmail SMTP                            |
| URL detection   | Custom heuristics, Google Safe Browsing API, VirusTotal API |
| Phone detection | `phonenumbers` + `pycountry` + Abstract Phone Validation API |

---

## 📁 Project Structure

```
tecktalks-cyber-eye/
├── frontend/
│   ├── html/
│   │   ├── index.html          # Landing page
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── scan_link.html
│   │   ├── scan_phone.html
│   │   ├── history.html
│   │   └── profile.html
│   ├── javaScript/
│   │   ├── signup.js
│   │   ├── login.js
│   │   ├── dashboard.js
│   │   ├── scan_link.js
│   │   ├── scan_phone.js
│   │   ├── history.js
│   │   └── profile.js
│   └── css/
│       └── style.css
│
├── backend/
│   ├── main.py                 # FastAPI app entry — registers all routers + CORS
│   ├── database.py             # SQLAlchemy engine, session, init_db()
│   ├── db_models.py            # User, UserProfile, ScanHistory ORM models
│   ├── crud.py                 # All DB read/write operations
│   ├── history.py              # GET /history, DELETE /history/{id}
│   ├── profile.py              # GET /profile, PATCH /profile
│   │
│   ├── signup/
│   │   ├── signup.py              # POST /signup
│   │   ├── verify_email.py        # POST /verify-email
│   │   ├── email_verification.py  # OTP generation + Gmail SMTP delivery
│   │   ├── email_security.py      # Disposable-email blocklist
│   │   ├── hashpass.py            # bcrypt hash helper
│   │   ├── validation.py          # Password rules
│   │   ├── user_validation.py     # Username rules
│   │   └── models.py
│   │
│   ├── login/
│   │   ├── login.py            # POST /login
│   │   ├── auth.py             # JWT create/verify + get_current_user
│   │   ├── hash.py             # bcrypt verify helper
│   │   └── models.py
│   │
│   ├── scanlink/
│   │   ├── scan_link.py        # POST /scan-link  (JWT-protected)
│   │   ├── detection.py        # Heuristic URL scoring
│   │   ├── google_safe.py      # Google Safe Browsing client
│   │   ├── virustotal.py       # VirusTotal v3 client
│   │   └── models.py
│   │
│   └── phonescan/
│       ├── scan_phone.py          # POST /scan-phone  (JWT-protected)
│       ├── countries.py           # GET /countries
│       ├── phone_utils.py         # E.164 normalization
│       ├── phone_validation.py    # phonenumbers-based validation
│       ├── phone_detection.py     # Local pattern scoring
│       ├── phone_api.py           # Abstract Phone Validation client
│       ├── phone_api_detection.py # Verdict logic from API response
│       └── models.py
│
├── database/
│   └── cybereye_database copy 2.sql   # Reference SQL schema
│
├── .env                        # Local secrets (NEVER commit)
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/jinan251/tecktalks-cyber-eye.git
cd tecktalks-cyber-eye
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root with the following keys:

```env
# Auth
SECRET_KEY=your_long_random_secret_here

# Gmail SMTP (use a Google App Password, not your normal password)
EMAIL_USER=youraddress@gmail.com
EMAIL_APP_PASSWORD=your_16_char_app_password

# External APIs
VIRUSTOTAL_API_KEY=your_virustotal_v3_key
GOOGLE_SAFE_API_KEY=your_google_safe_browsing_key
ABSTRACT_API_KEY=your_abstract_phone_api_key
```

> ⚠️ Never commit your `.env` to GitHub. Add it to `.gitignore` if it isn't already.

### 5. Run the backend server

From the **project root** (the folder containing `backend/`), run:

```bash
uvicorn backend.main:app --reload
```

The API will be available at:
- **Base URL:** `http://127.0.0.1:8000`
- **Interactive docs (Swagger UI):** `http://127.0.0.1:8000/docs`
- **Alternative docs (ReDoc):** `http://127.0.0.1:8000/redoc`

The SQLite database `cyber_eye.db` is created automatically on first run.

### 6. Open the frontend

Open `frontend/html/index.html` in your browser, or use the VS Code **Live Server** extension to serve the `frontend/` folder. CORS is enabled in the backend so the two can talk to each other.

---

## 📡 API Endpoints

| Method | Path                  | Auth | Purpose                                          |
|--------|-----------------------|------|--------------------------------------------------|
| POST   | `/signup`             | —    | Register and send OTP to email                   |
| POST   | `/verify-email`       | —    | Verify OTP, return JWT                           |
| POST   | `/login`              | —    | Log in, return JWT                               |
| POST   | `/scan-link`          | JWT  | Scan a URL, save result to history               |
| POST   | `/scan-phone`         | JWT  | Scan a phone number, save result to history     |
| GET    | `/countries`          | —    | List all countries with ISO code and phone code |
| GET    | `/history`            | JWT  | Paginated scan history (filters: type, result)   |
| DELETE | `/history/{scan_id}`  | JWT  | Delete one of the user's own scans               |
| GET    | `/profile`            | JWT  | Get user + profile + scan stats                  |
| PATCH  | `/profile`            | JWT  | Update full_name / bio / avatar_url              |

Authenticated endpoints expect `Authorization: Bearer <token>` from `/login` or `/verify-email`.

---

## 🔍 How Detection Works

### URL pipeline (`/scan-link`)
1. **Heuristic scoring** — checks for IP-as-host, URL shorteners, brand spoofing,
   phishing keywords, suspicious TLDs, `@` in URL, low-entropy hostnames, etc.
2. **Google Safe Browsing** — checks the URL against Google's threat lists.
3. **VirusTotal v3** — pulls the latest analysis stats for the URL.
4. **Final verdict** — Google or VirusTotal `phishing` overrides everything;
   otherwise the highest-severity signal wins. Result saved to `scan_history`.

### Phone pipeline (`/scan-phone`)
1. **Normalize** to E.164 with `phonenumbers`.
2. **Local pattern check** — length, repeated digits, sequential patterns.
3. **External phone API** — carrier, line type, validity (VoIP flagged as suspicious).
4. **Final verdict** — invalid format → `invalid`; phishing/suspicious from any
   layer escalates accordingly; otherwise `safe` or `unknown`. Saved to history.

---

## 🗄️ Database Schema (summary)

- **`users`** — id, username, email, password_hash, is_verified, verification_token, token_expiry, created_at
- **`user_profiles`** — id, user_id (FK, unique), full_name, bio, avatar_url, created_at, updated_at
- **`scan_history`** — id, user_id (FK, nullable), type (`url` | `phone`), input_value, result (`safe` | `suspicious` | `phishing` | `unknown`), timestamp

Cascading deletes are enabled on `user_profiles`; `scan_history.user_id` is set to NULL if the user is deleted.

---

## ⚠️ Current Limitations

- Detection accuracy depends on third-party APIs (Google Safe Browsing, VirusTotal, Abstract).
- SQLite is fine for development and small deployments; switch to PostgreSQL for production.
- OTP delivery uses Gmail SMTP — replace with a transactional provider (SendGrid, Mailgun, SES) for real users.
- Not a replacement for full antivirus or endpoint protection.

---

## 🗺️ Roadmap

- [ ] AI-powered threat pattern recognition (risk score + reasoning)
- [ ] Analytics dashboard for phishing trends
- [ ] Browser extension for one-click scanning
- [ ] Multi-language support
- [ ] Rate limiting and CAPTCHA on signup / scan endpoints

---

## 👥 Team

| Role                  | Member |
|-----------------------|--------|
| Frontend              | Amar   |
| Backend               | Nie    |
| Database              | Sana   |
| Testing & Integration | Jinan  |

Project coordination via Notion workspace and jira and GitHub: `tecktalks-cyber-eye`.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss
what you'd like to improve or add. Please work on a feature branch and avoid
direct commits to shared files like `backend/main.py`.

---

## 📄 License

MIT
