from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response
from flask_cors import CORS
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
import pickle
import jwt
import json
import os
from datetime import datetime, timedelta
import time
from googletrans import Translator

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
CORS(app)

# Global variables
camera = None
detection_active = False
current_prediction = ""

translator = Translator()

# MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

# Load the trained model
try:
    with open('body_language.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully")
except:
    print("Model not found. Please ensure body_language.pkl is in the project directory")
    model = None

# User & Feedback file setup
USERS_FILE = 'users.json'
FEEDBACK_FILE = 'feedback.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return []

def save_feedback(feedback_list):
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_list, f, indent=2)

def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

class SignLanguageDetector:
    def __init__(self):
        self.prev_prediction = ""
        self.stable_counter = 0
        self.STABILITY_THRESHOLD = 5
        self.holistic = mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detect_sign(self, frame):
        global current_prediction

        if model is None:
            return frame

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

        try:
            if results.right_hand_landmarks or results.left_hand_landmarks:
                right_row = [0] * 84
                left_row = [0] * 84

                if results.right_hand_landmarks:
                    right = results.right_hand_landmarks.landmark
                    right_row = list(np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in right]).flatten())

                if results.left_hand_landmarks:
                    left = results.left_hand_landmarks.landmark
                    left_row = list(np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in left]).flatten())

                row = right_row + left_row
                X = pd.DataFrame([row])
                prediction = model.predict(X)[0]
                confidence = model.predict_proba(X)[0][np.argmax(model.predict_proba(X)[0])]

                if prediction == self.prev_prediction:
                    self.stable_counter += 1
                else:
                    self.stable_counter = 0
                    self.prev_prediction = prediction

                if self.stable_counter > self.STABILITY_THRESHOLD:
                    current_prediction = prediction
                    cv2.rectangle(image, (10, 10), (400, 60), (0, 0, 0), -1)
                    cv2.putText(image, f'Sign: {prediction}', (20, 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        except Exception as e:
            print(f"Detection error: {e}")

        return image

detector = SignLanguageDetector()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        users = load_users()
        if username in users:
            return jsonify({'success': False, 'message': 'Username already exists'})

        users[username] = password
        save_users(users)
        return jsonify({'success': True, 'message': 'Registration successful'})

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        users = load_users()
        if username in users and users[username] == password:
            token = generate_token(username)
            return jsonify({'success': True, 'token': token})

        return jsonify({'success': False, 'message': 'Invalid credentials'})

    return render_template('login.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        data = request.get_json()
        feedback_text = data.get('feedback')

        feedback_list = load_feedback()
        feedback_entry = {
            'feedback': feedback_text,
            'timestamp': datetime.now().isoformat()
        }
        feedback_list.append(feedback_entry)
        save_feedback(feedback_list)

        return jsonify({'success': True, 'message': 'Feedback submitted successfully'})

    return render_template('feedback.html')

@app.route('/detect')
def detect():
    return render_template('detect.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global camera, detection_active

    token = request.headers.get('Authorization')
    if not token or not verify_token(token.replace('Bearer ', '')):
        return jsonify({'success': False, 'message': 'Unauthorized'})

    try:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        detection_active = True
        return jsonify({'success': True, 'message': 'Detection started'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global camera, detection_active

    detection_active = False
    if camera:
        camera.release()
        camera = None

    return jsonify({'success': True, 'message': 'Detection stopped'})

@app.route('/video_feed')
def video_feed():
    def generate_frames():
        global camera, detection_active

        while detection_active and camera and camera.isOpened():
            success, frame = camera.read()
            if not success:
                break

            processed_frame = detector.detect_sign(frame)

            try:
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                print("Encoding error:", e)
                continue

            time.sleep(0.03)  # ~30 FPS

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_prediction')
def get_prediction():
    global current_prediction
    return jsonify({
        'prediction': current_prediction
    })

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('language', 'hi')

    lang_codes = {
        'hindi': 'hi',
        'kannada': 'kn',
        'malayalam': 'ml'
    }

    target_code = lang_codes.get(target_lang.lower(), 'hi')

    try:
        translated = translator.translate(text, dest=target_code)
        return jsonify({
            'success': True,
            'translated_text': translated.text,
            'original_text': text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
