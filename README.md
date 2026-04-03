# CyberEye 🛡️
Smart cybersecurity detection at your fingertips. CyberEye helps users check 
URLs, links, and phone numbers in real-time to identify phishing attempts, 
fraud, and malicious content — before it's too late.

## What It Does
- 🔗 Detects phishing and malicious URLs instantly
- 📞 Verifies phone numbers for fraud or suspicious activity
- ⚡ Delivers real-time threat verdicts with zero technical knowledge needed
- 🧠 Combines multiple APIs for higher detection accuracy

## Why It Matters
Every day, thousands of people fall victim to phishing scams, fake links, and 
fraudulent calls. CyberEye gives everyday users a simple tool to verify before 
they click, call, or share — making the internet safer for everyone.

## Tech Stack
| Layer      | Technology                                         |
|------------|----------------------------------------------------|
| Frontend   | HTML, CSS, JavaScript                              |
| Backend    | Python, Node.js, PHP                               |
| Database   | JSON, SQLite                                       |
| APIs       | Google Safe Browsing, VirusTotal, Phone Validation |

## How It Works
1. Enter a URL, link, or phone number
2. CyberEye analyzes it in real-time across multiple detection sources
3. Get an instant verdict: ✅ Safe | ⚠️ Suspicious | 🚨 Dangerous

## Installation
```bash
git clone https://github.com/yourusername/CyberEye.git
cd CyberEye
pip install -r requirements.txt
python app.py
```

## Project Structure
```
CyberEye/
├── static/          # Frontend assets
├── templates/       # HTML pages
├── routes/          # API route handlers
├── utils/           # Detection logic
├── app.py           # Main backend
└── requirements.txt
```

## Current Limitations
- Detection relies on third-party APIs (Google Safe Browsing, VirusTotal)
- Not a replacement for full antivirus software
- Phone number fraud detection depends on available database coverage

## Future Plans
- [ ] AI-powered threat pattern recognition
- [ ] Analytics dashboard for phishing trends
- [ ] Browser extension for on-the-go protection
- [ ] Multi-language support

## Contributing
Pull requests are welcome. For major changes, open an issue first to discuss 
what you'd like to improve or add.

## License
MIT
