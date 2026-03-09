from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import random
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database configuration
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'language_learning.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class SpeechError(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_agent = db.Column(db.String(500))
    browser = db.Column(db.String(100))
    error_type = db.Column(db.String(100))
    error_message = db.Column(db.Text)
    language = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True)
    total_score = db.Column(db.Integer, default=0)
    languages_data = db.Column(db.Text)  # JSON string
    badges = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create database tables
with app.app_context():
    db.create_all()

# Language phrases database
PHRASES = {
    "bodo": {
        "beginner": [
            {"id": 1, "phrase": "नमस्ते", "meaning": "Hello", "phonetic": "na-ma-ste"},
            {"id": 2, "phrase": "मोन", "meaning": "What", "phonetic": "mon"},
            {"id": 3, "phrase": "हाँ", "meaning": "Yes", "phonetic": "han"},
            {"id": 4, "phrase": "नाइ", "meaning": "No", "phonetic": "nai"},
            {"id": 5, "phrase": "बायदंग", "meaning": "Thank you", "phonetic": "bai-dang"},
            {"id": 6, "phrase": "अनानी", "meaning": "Mother", "phonetic": "a-na-ni"},
            {"id": 7, "phrase": "बाबा", "meaning": "Father", "phonetic": "ba-ba"},
            {"id": 8, "phrase": "दाइ", "meaning": "Sister", "phonetic": "dai"},
            {"id": 9, "phrase": "आवा", "meaning": "Come", "phonetic": "a-va"},
            {"id": 10, "phrase": "जाब", "meaning": "Go", "phonetic": "ja-b"}
        ],
        "intermediate": [
            {"id": 11, "phrase": "अंग आयद गोजान", "meaning": "How are you?", "phonetic": "ang ai-dan go-zan"},
            {"id": 12, "phrase": "मोनसे खाबर हांव?", "meaning": "What's your name?", "phonetic": "mon-se kha-bar han"},
            {"id": 13, "phrase": "नाथार बिसाम", "meaning": "Good morning", "phonetic": "na-thar bi-sam"},
            {"id": 14, "phrase": "हांसे सेरेन", "meaning": "I understand", "phonetic": "han-se se-ren"},
            {"id": 15, "phrase": "मोन नाइ बूझाय", "meaning": "I don't understand", "phonetic": "mon nai bu-zhai"}
        ]
    },
    "mizo": {
        "beginner": [
            {"id": 1, "phrase": "Chawle", "meaning": "Hello", "phonetic": "chaw-le"},
            {"id": 2, "phrase": "En", "meaning": "What", "phonetic": "en"},
            {"id": 3, "phrase": "Aw", "meaning": "Yes", "phonetic": "aw"},
            {"id": 4, "phrase": "Ih", "meaning": "No", "phonetic": "ih"},
            {"id": 5, "phrase": "Ka lawm e", "meaning": "Thank you", "phonetic": "ka lawm e"},
            {"id": 6, "phrase": "Nu", "meaning": "Mother", "phonetic": "nu"},
            {"id": 7, "phrase": "Pa", "meaning": "Father", "phonetic": "pa"},
            {"id": 8, "phrase": "Unau", "meaning": "Friend", "phonetic": "u-nau"},
            {"id": 9, "phrase": "la", "meaning": "Come", "phonetic": "la"},
            {"id": 10, "phrase": "chan", "meaning": "Go", "phonetic": "chan"}
        ],
        "intermediate": [
            {"id": 11, "phrase": "Nge maw i hlim?", "meaning": "How are you?", "phonetic": "nge maw i hlim"},
            {"id": 12, "phrase": "I hming chu eng nge?", "meaning": "What's your name?", "phonetic": "i hming chu eng nge"},
            {"id": 13, "phrase": "Zin tura lo vawng rawh", "meaning": "Let's go", "phonetic": "zin tura lo vawng rawh"},
            {"id": 14, "phrase": "Ka inhria", "meaning": "I understand", "phonetic": "ka inhria"},
            {"id": 15, "phrase": "Ka inhriat lo", "meaning": "I don't understand", "phonetic": "ka inhriat lo"}
        ]
    },
    "dogri": {
        "beginner": [
            {"id": 1, "phrase": "सलाम", "meaning": "Hello", "phonetic": "sa-laam"},
            {"id": 2, "phrase": "की", "meaning": "What", "phonetic": "kee"},
            {"id": 3, "phrase": "हाँ", "meaning": "Yes", "phonetic": "haan"},
            {"id": 4, "phrase": "नहीं", "meaning": "No", "phonetic": "na-heen"},
            {"id": 5, "phrase": "धन्यवाद", "meaning": "Thank you", "phonetic": "dhan-ya-vaad"},
            {"id": 6, "phrase": "माता", "meaning": "Mother", "phonetic": "maa-taa"},
            {"id": 7, "phrase": "पिता", "meaning": "Father", "phonetic": "pi-taa"},
            {"id": 8, "phrase": "भगत", "meaning": "Friend", "phonetic": "bhag-ta"},
            {"id": 9, "phrase": "आओ", "meaning": "Come", "phonetic": "aa-o"},
            {"id": 10, "phrase": "जा", "meaning": "Go", "phonetic": "jaa"}
        ],
        "intermediate": [
            {"id": 11, "phrase": "तेरा नाम की ऐ?", "meaning": "What's your name?", "phonetic": "tera naam kee ai"},
            {"id": 12, "phrase": "तूनै विच कैसे?", "meaning": "How are you?", "phonetic": "toonai vich kaise"},
            {"id": 13, "phrase": "सुप्रभात", "meaning": "Good morning", "phonetic": "su-pra-bhaat"},
            {"id": 14, "phrase": "मैं समझदा ऐ", "meaning": "I understand", "phonetic": "main sam-jha-da ai"},
            {"id": 15, "phrase": "मैं नहीं समझदा", "meaning": "I don't understand", "phonetic": "main na-heen sam-jha-da"}
        ]
    }
}

# User data storage (in-memory for demo)
users = {}
user_scores = {}

# Badges/Achievements
BADGES = {
    "first_lesson": {"name": "First Steps", "description": "Complete your first lesson", "icon": "🎯"},
    "perfect_score": {"name": "Perfect Pronunciation", "description": "Get 100% on a phrase", "icon": "⭐"},
    "language_master": {"name": "Language Master", "description": "Complete all lessons in a language", "icon": "🏆"},
    "week_streak": {"name": "Weekly Warrior", "description": "Practice for 7 days in a row", "icon": "🔥"},
    "speed_demon": {"name": "Speed Demon", "description": "Answer 5 questions in under 30 seconds", "icon": "⚡"},
    "dedicated_learner": {"name": "Dedicated Learner", "description": "Complete 50 phrases", "icon": "📚"}
}

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get available languages"""
    languages = [
        {"id": "bodo", "name": "Bodo", "native_name": "बड़ो", "flag": "🇮🇳", "description": "A language of Assam, India"},
        {"id": "mizo", "name": "Mizo", "native_name": "Mizo", "flag": "🇮🇳", "description": "A language of Mizoram, India"},
        {"id": "dogri", "name": "Dogri", "native_name": "डोगरी", "flag": "🇮🇳", "description": "A language of Jammu & Kashmir, India"}
    ]
    return jsonify(languages)

@app.route('/api/levels/<language>', methods=['GET'])
def get_levels(language):
    """Get available levels for a language"""
    if language not in PHRASES:
        return jsonify({"error": "Language not found"}), 404
    
    levels = [
        {"id": "beginner", "name": "Beginner", "description": "Learn basic phrases", "phrases_count": len(PHRASES[language]["beginner"])},
        {"id": "intermediate", "name": "Intermediate", "description": "Practice conversations", "phrases_count": len(PHRASES[language]["intermediate"])}
    ]
    return jsonify(levels)

@app.route('/api/phrases/<language>/<level>', methods=['GET'])
def get_phrases(language, level):
    """Get phrases for a specific language and level"""
    if language not in PHRASES:
        return jsonify({"error": "Language not found"}), 404
    
    if level not in PHRASES[language]:
        return jsonify({"error": "Level not found"}), 404
    
    return jsonify(PHRASES[language][level])

@app.route('/api/evaluate', methods=['POST'])
def evaluate_pronunciation():
    """Evaluate user pronunciation using AI simulation"""
    try:
        data = request.json
        if data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        
        language = data.get('language')
        phrase_id = data.get('phrase_id')
        user_speech = (data.get('user_speech') or '').lower().strip()

        # Find the original phrase
        phrase_text = ""
        if language in PHRASES:
            for level in PHRASES[language]:
                for phrase in PHRASES[language][level]:
                    if phrase['id'] == phrase_id:
                        phrase_text = phrase['phrase'].lower()
                        break

        if not phrase_text:
            return jsonify({"error": "Phrase not found"}), 404

        # AI-powered pronunciation evaluation (simulated)
        score = calculate_pronunciation_score(phrase_text, user_speech)

        # Generate feedback based on score
        if score >= 90:
            feedback = "Excellent! Your pronunciation is nearly perfect! 🌟"
            emoji = "🎉"
        elif score >= 70:
            feedback = "Good job! Keep practicing to improve further! 👍"
            emoji = "💪"
        elif score >= 50:
            feedback = "Not bad! Try to match the pronunciation more closely. 💬"
            emoji = "📢"
        else:
            feedback = "Keep practicing! Listen carefully and try again. 🎯"
            emoji = "💡"

        return jsonify({
            "score": score,
            "feedback": feedback,
            "emoji": emoji,
            "original_phrase": phrase_text,
            "user_speech": user_speech
        })

    except Exception as e:
        # Log unexpected errors
        log_speech_error("evaluation_error", str(e), request.headers.get('User-Agent', 'Unknown'))
        return jsonify({"error": "Evaluation failed", "details": str(e)}), 500

def calculate_pronunciation_score(original, spoken):
    """Calculate pronunciation score using basic string matching"""
    if not spoken:
        return 0

    # Simple character-based similarity
    original_clean = ''.join(c.lower() for c in original if c.isalnum())
    spoken_clean = ''.join(c.lower() for c in spoken if c.isalnum())

    if original_clean == spoken_clean:
        return 100

    # Calculate similarity using common characters
    common = sum(1 for c in original_clean if c in spoken_clean)
    max_len = max(len(original_clean), len(spoken_clean))

    if max_len == 0:
        return 0

    similarity = (common / max_len) * 100

    # Bonus for getting the start right
    if original_clean[:2] == spoken_clean[:2]:
        similarity += 10

    return min(100, int(similarity))

def log_speech_error(error_type, error_message, user_agent, language=None):
    """Log speech recognition errors to database"""
    try:
        # Extract browser info from user agent
        browser = "Unknown"
        if "Chrome" in user_agent and "Edg" not in user_agent:
            browser = "Chrome"
        elif "Edg" in user_agent:
            browser = "Edge"
        elif "Firefox" in user_agent:
            browser = "Firefox"
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            browser = "Safari"
        elif "Opera" in user_agent:
            browser = "Opera"

        error = SpeechError(
            user_agent=user_agent,
            browser=browser,
            error_type=error_type,
            error_message=error_message,
            language=language
        )
        db.session.add(error)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log error: {e}")

@app.route('/api/log-speech-error', methods=['POST'])
def log_speech_error_endpoint():
    """Endpoint to log speech recognition errors from frontend"""
    try:
        data = request.json
        if data is None:
            return jsonify({"success": False, "error": "Invalid JSON data"}), 400
        
        error_type = data.get('error_type')
        error_message = data.get('error_message')
        language = data.get('language')
        user_agent = request.headers.get('User-Agent', 'Unknown')

        log_speech_error(error_type, error_message, user_agent, language)

        return jsonify({"success": True, "message": "Error logged successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/speech-error-stats', methods=['GET'])
def get_speech_error_stats():
    """Get speech recognition error statistics"""
    try:
        # Get error counts by browser
        browser_stats = db.session.query(
            SpeechError.browser,
            db.func.count(SpeechError.id).label('count')
        ).group_by(SpeechError.browser).all()

        # Get error counts by type
        error_type_stats = db.session.query(
            SpeechError.error_type,
            db.func.count(SpeechError.id).label('count')
        ).group_by(SpeechError.error_type).all()

        # Get recent errors (last 100)
        recent_errors = SpeechError.query.order_by(SpeechError.timestamp.desc()).limit(100).all()

        return jsonify({
            "browser_stats": [{"browser": b, "count": c} for b, c in browser_stats],
            "error_type_stats": [{"error_type": e, "count": c} for e, c in error_type_stats],
            "recent_errors": [{
                "id": e.id,
                "browser": e.browser,
                "error_type": e.error_type,
                "error_message": e.error_message,
                "language": e.language,
                "timestamp": e.timestamp.isoformat()
            } for e in recent_errors]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/score', methods=['POST'])
def save_score():
    """Save user score"""
    data = request.json
    if data is None:
        return jsonify({"success": False, "error": "Invalid JSON data"}), 400
    
    user_id = data.get('user_id', 'default_user')
    language = data.get('language')
    level = data.get('level')
    score = data.get('score')
    phrase_id = data.get('phrase_id')
    
    if user_id not in users:
        users[user_id] = {
            "total_score": 0,
            "languages": {},
            "badges": [],
            "streak": 0,
            "last_practice": None
        }
    
    user = users[user_id]
    user["total_score"] += score
    
    if language not in user["languages"]:
        user["languages"][language] = {
            "total_score": 0,
            "phrases_completed": [],
            "levels_completed": []
        }
    
    lang_data = user["languages"][language]
    lang_data["total_score"] += score
    
    if phrase_id not in lang_data["phrases_completed"]:
        lang_data["phrases_completed"].append(phrase_id)
    
    # Check for badges
    check_badges(user, lang_data, score)
    
    return jsonify({
        "success": True,
        "total_score": user["total_score"],
        "badges_earned": user["badges"]
    })

def check_badges(user, lang_data, score):
    """Check and award badges"""
    # First lesson badge
    if len(lang_data["phrases_completed"]) >= 1:
        if "first_lesson" not in user["badges"]:
            user["badges"].append("first_lesson")
    
    # Perfect score badge
    if score >= 100:
        if "perfect_score" not in user["badges"]:
            user["badges"].append("perfect_score")
    
    # Dedicated learner badge
    if len(lang_data["phrases_completed"]) >= 50:
        if "dedicated_learner" not in user["badges"]:
            user["badges"].append("dedicated_learner")

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user_progress(user_id):
    """Get user progress"""
    if user_id not in users:
        return jsonify({
            "total_score": 0,
            "languages": {},
            "badges": [],
            "streak": 0
        })
    
    return jsonify(users[user_id])

@app.route('/api/badges', methods=['GET'])
def get_badges():
    """Get all available badges"""
    return jsonify(BADGES)

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """Text-to-Speech endpoint (for reference - handled client-side)"""
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid JSON data"}), 400
    
    text = data.get('text', '')
    language = data.get('language', 'en')
    
    # Return language code mapping for TTS
    lang_codes = {
        "bodo": "bn",  # Bodo uses Bengali script
        "mizo": "en",
        "dogri": "hi"
    }
    
    return jsonify({
        "text": text,
        "language_code": lang_codes.get(language, "en"),
        "message": "Use browser Web Speech API for TTS"
    })

@app.route('/', methods=['GET'])
def index():
    """Homepage - API information"""
    return jsonify({
        "message": "AI Language Learning API",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
