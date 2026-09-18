export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'SignSpeak AI';

export const ROUTES = {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    DETECTION: '/detection',
    FEEDBACK: '/feedback',
};

export const SUPPORTED_LANGUAGES = [
    { code: 'hindi', label: 'Hindi', flag: '🇮🇳' },
    { code: 'kannada', label: 'Kannada', flag: '🇮🇳' },
    { code: 'malayalam', label: 'Malayalam', flag: '🇮🇳' },
];

export const PREDICTION_POLL_INTERVAL = 100; // ms
export const TOKEN_KEY = 'signspeak_token';
