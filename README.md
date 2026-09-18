# SignSpeak AI - Real-Time Sign Language Translation System

![SignSpeak AI](https://img.shields.io/badge/AI-Powered-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange) ![Python](https://img.shields.io/badge/Python-3.12-yellow) ![React](https://img.shields.io/badge/React-18-61dafb)

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Technical Architecture](#technical-architecture)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [API Documentation](#api-documentation)
- [Machine Learning Model](#machine-learning-model)
- [Frontend Features](#frontend-features)
- [Security Features](#security-features)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

**SignSpeak AI** is a real-time sign language translation system powered by artificial intelligence. The application uses computer vision and machine learning to detect hand gestures through a webcam, recognize sign language patterns, and translate them into text with multilingual support. This accessibility-first solution aims to break communication barriers for the deaf and hard-of-hearing community.

### Mission
To make technology accessible for everyone by providing seamless, real-time sign language translation that enables effective communication between sign language users and non-signers.

---

## ✨ Key Features

### 🎥 Real-Time Sign Language Detection
- **Live Video Processing**: Captures webcam feed at ~30 FPS for smooth detection
- **Hand Landmark Tracking**: Uses MediaPipe Holistic to track 21 landmarks on each hand (42 total)
- **Bilateral Detection**: Supports both left and right hand gesture recognition
- **Stability Algorithm**: Implements a stability threshold (5 consecutive frames) to prevent false positives
- **Visual Feedback**: Draws hand landmarks and connections on video feed in real-time

### 🌐 Multilingual Translation
- **Supported Languages**: Hindi (हिंदी), Kannada (ಕನ್ನಡ), Malayalam (മലയാളം)
- **Google Translate Integration**: Real-time text translation via googletrans
- **Text-to-Speech**: Browser-based speech synthesis for translated text

### 🔐 User Authentication
- **JWT-based Authentication**: Secure token-based auth with 24-hour expiration
- **Password Security**: bcrypt hashing with transparent migration from legacy passwords
- **Protected Routes**: Detection features require authentication

### 🎨 Modern Frontend
- **React 18** with Vite for fast development
- **Framer Motion** animations
- **Tailwind CSS** styling
- **Responsive Design** for all screen sizes

---

## 🏗️ Technical Architecture

```
React/Vite Frontend (port 3000/5173)
        ↓ Axios REST API
FastAPI Backend (port 8000)
        ↓
OpenCV + MediaPipe + Scikit-learn
        ↓
Prediction → React UI → Web Speech API
```

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Web framework (async, auto-docs) |
| **Uvicorn** | ASGI server |
| **Pydantic** | Request/response validation |
| **PyJWT** | JWT token handling |
| **passlib + bcrypt** | Password hashing |
| **OpenCV** | Video capture and processing |
| **MediaPipe** | Hand landmark detection |
| **Scikit-learn** | ML classification |
| **googletrans** | Text translation |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **Vite** | Build tool |
| **Tailwind CSS** | Styling |
| **Axios** | HTTP client |
| **Framer Motion** | Animations |
| **React Router** | Client-side routing |

---

## 💻 System Requirements

- Python 3.11+
- Node.js 18+
- Webcam (for detection features)
- pip (Python package manager)

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Signspeak-AI.git
cd Signspeak-AI
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings (especially JWT_SECRET_KEY)
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application

**Start Backend** (from project root):
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend** (in a separate terminal):
```bash
cd frontend
npm run dev
```

### 5. Access the Application
| Service | URL |
|---|---|
| **Frontend** | http://localhost:5173 or http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **Swagger UI (API Docs)** | http://localhost:8000/docs |
| **ReDoc (API Docs)** | http://localhost:8000/redoc |

---

## 📁 Project Structure

```
Signspeak-AI/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Pydantic Settings configuration
│   │   ├── security.py          # JWT & password hashing
│   │   ├── dependencies.py      # Auth dependency injection
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── routes/
│   │   │   ├── auth.py          # /register, /login
│   │   │   ├── detection.py     # /start_detection, /stop_detection, /video_feed, /get_prediction
│   │   │   ├── translation.py   # /translate
│   │   │   └── feedback.py      # /feedback
│   │   └── services/
│   │       ├── user_service.py       # User CRUD operations
│   │       ├── feedback_service.py   # Feedback storage
│   │       ├── detection_service.py  # ML pipeline & camera management
│   │       └── translation_service.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── context/AuthContext.jsx
│   │   ├── services/api.js
│   │   ├── hooks/usePrediction.js
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Detection.jsx
│   │   │   └── Feedback.jsx
│   │   └── components/
│   │       └── ProtectedRoute.jsx
│   ├── .env
│   └── package.json
├── body_language.pkl            # Trained ML model
├── users.json                   # User storage
├── feedback.json                # Feedback storage
└── README.md
```

---

## 🔌 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API info and status |
| `POST` | `/register` | Register new user |
| `POST` | `/login` | Login and get JWT token |
| `POST` | `/feedback` | Submit feedback |

### Protected Endpoints (require JWT)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/start_detection` | Start webcam and detection |

### Detection Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/stop_detection` | Stop detection |
| `GET` | `/video_feed` | MJPEG video stream |
| `GET` | `/get_prediction` | Current sign prediction |
| `POST` | `/translate` | Translate text |

---

## 📖 API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs — Interactive API explorer
- **ReDoc**: http://localhost:8000/redoc — Clean API reference

---

## 🧠 Machine Learning Model

- **Model File**: `body_language.pkl`
- **Framework**: Scikit-learn classifier
- **Features**: 168 total (84 per hand × 2 hands)
  - 21 landmarks per hand
  - 4 values per landmark (x, y, z, visibility)
- **Stability**: 5 consecutive identical predictions required
- **Input**: MediaPipe Holistic hand landmarks
- **Resolution**: 640×480 at ~30 FPS

---

## 🔐 Security Features

- **JWT Authentication**: HS256 tokens with 24-hour expiration
- **Password Hashing**: bcrypt via passlib (with transparent upgrade from legacy plaintext)
- **CORS**: Restricted to configured frontend origins
- **Environment Variables**: Secrets stored in `.env` (not committed to git)

---

## ⚙️ Configuration

All configuration is via environment variables in `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | `your-secret-key-here` | Secret for JWT signing |
| `JWT_EXPIRATION_HOURS` | `24` | JWT token lifetime |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Allowed CORS origins |

---

## 🔧 Troubleshooting

### Camera not working
- Ensure no other application is using the webcam
- Check camera permissions in your OS settings
- On Windows, the app uses `CAP_DSHOW` backend

### mediapipe installation issues
- Requires Python 3.11+
- On some systems: `pip install mediapipe --no-cache-dir`

### googletrans errors
- The `googletrans==4.0.0rc1` package requires specific pinned dependencies
- If translation fails, check your internet connection

### CORS errors
- Verify `CORS_ORIGINS` in `backend/.env` matches your frontend URL
- Default allows `http://localhost:5173` and `http://localhost:3000`

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is for educational purposes.

backend\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
