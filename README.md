# HashChat

A lightweight real-time private-room chat application built with Flask, Socket.IO and SQLite.

HashChat allows users to choose a nickname, create private rooms, and chat instantly without registration.

---

## Features

• Nickname-based access (no accounts)
• Private chat rooms by port & name
• Real-time messaging with WebSockets
• Persistent user sessions
• Mobile responsive UI
• Dark purple gradient UI
• Logout and Leave Room support

---

## Installation

### 1. Clone the repository

git clone https://github.com/Rasa8877/HashChat.git  
cd HashChat

### 2. Create virtual environment

python -m venv .venv  
source .venv/bin/activate  # Linux  
.venv\Scripts\activate     # Windows

### 3. Install dependencies

pip install -r requirements.txt

---

## Run locally

python app.py

Open in browser:

http://127.0.0.1:5000

---

## Production

gunicorn -k eventlet -w 1 app:app --bind 0.0.0.0:8000

---

## Tech Stack

• Flask  
• Flask-SocketIO  
• SQLite  
• Tailwind CSS  

---

## License

MIT License
