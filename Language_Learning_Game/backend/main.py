from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Load words from data.json
def load_words():
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'data.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

WORDS_DATA = load_words()

# Get all languages
@app.route('/api/languages', methods=['GET'])
def get_languages():
    languages = []
    for lang_code, lang_data in WORDS_DATA.items():
        languages.append({
            'id': lang_code,
            'name': lang_data['name'],
            'native_name': lang_data['native_name'],
            'words_count': len(lang_data['words'])
        })
    return jsonify(languages)

# Get words for a specific language
@app.route('/api/words/<language>', methods=['GET'])
def get_words(language):
    if language not in WORDS_DATA:
        return jsonify({'error': 'Language not found'}), 404
    
    return jsonify(WORDS_DATA[language]['words'])

# Get a random word for quiz
@app.route('/api/quiz/<language>', methods=['GET'])
def get_quiz_word(language):
    if language not in WORDS_DATA:
        return jsonify({'error': 'Language not found'}), 404
    
    import random
    words = WORDS_DATA[language]['words']
    word = random.choice(words)
    return jsonify(word)

# Check answer
@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    language = data.get('language')
    word_id = data.get('word_id')
    user_answer = data.get('answer', '').strip().lower()
    
    if language not in WORDS_DATA:
        return jsonify({'error': 'Language not found'}), 404
    
    # Find the word
    correct_word = None
    for word in WORDS_DATA[language]['words']:
        if word['id'] == word_id:
            correct_word = word
            break
    
    if not correct_word:
        return jsonify({'error': 'Word not found'}), 404
    
    # Check answer (case-insensitive)
    is_correct = user_answer == correct_word['translation'].lower()
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct_word['translation'],
        'word': correct_word['word']
    })

# Get user progress
@app.route('/api/progress/<user_id>', methods=['GET'])
def get_progress(user_id):
    # In a real app, this would read from a database
    return jsonify({
        'user_id': user_id,
        'score': 0,
        'words_learned': 0,
        'streak': 0
    })

# Save user progress
@app.route('/api/progress', methods=['POST'])
def save_progress():
    data = request.json
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    user_id = data.get('user_id')
    score = data.get('score', 0)
    words_learned = data.get('words_learned', 0)
    
    # In a real app, this would save to a database
    return jsonify({
        'success': True,
        'user_id': user_id,
        'score': score,
        'words_learned': words_learned
    })

if __name__ == '__main__':
    import sys
    port = 5000
    if len(sys.argv) > 2 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    app.run(debug=True, port=port)
