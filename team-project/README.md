# AI-Powered Language Learning Game

An innovative AI-based mobile application that helps users learn Bodo, Mizo, and Dogri languages through voice interaction, pronunciation scoring, and gamification.

## Features

- 🎯 **Voice-based Learning**: Listen to phrases and practice speaking
- 🤖 **AI Pronunciation Evaluation**: Get instant feedback on your pronunciation
- 🏆 **Gamification**: Earn points, badges, and track your progress
- 📚 **3 Languages**: Bodo, Mizo, and Dogri
- 🌱 **Multiple Levels**: Beginner and Intermediate levels

## Technology Stack

- **Frontend**: React.js with Web Speech API
- **Backend**: Python with Flask
- **Speech Processing**: Web Speech API (TTS/ASR)
- **AI Evaluation**: String matching algorithm (simulated transformer)

## Project Structure

```
team-project/
├── backend/           # Flask backend
│   ├── app.py         # Main backend application
│   └── requirements.txt
├── frontend/          # React.js frontend
│   ├── public/
│   ├── src/
│   │   ├── App.js     # Main React component
│   │   ├── index.js   # Entry point
│   │   └── index.css  # Styles
│   └── package.json
├── README.md
└── TODO.md
```

## Installation & Setup

### Prerequisites
- Node.js (v18 or higher)
- Python (v3.8 or higher)
- npm

### Backend Setup

```
bash
cd team-project/backend
pip install -r requirements.txt
python app.py
```

The backend will run on http://localhost:5000

### Frontend Setup

```
bash
cd team-project/frontend
npm install
npm start
```

The frontend will run on http://localhost:3000

## How to Use

1. Open the application in your browser
2. Click "Start Learning"
3. Choose a language (Bodo, Mizo, or Dogri)
4. Select a level (Beginner or Intermediate)
5. Click "Start Game"
6. Listen to the phrase using the "Listen" button
7. Click "Speak Now" and repeat the phrase
8. Get instant feedback on your pronunciation
9. Earn points and badges as you progress!

## API Endpoints

- `GET /api/languages` - Get available languages
- `GET /api/levels/<language>` - Get levels for a language
- `GET /api/phrases/<language>/<level>` - Get phrases
- `POST /api/evaluate` - Evaluate pronunciation
- `POST /api/save_score` - Save user score
- `GET /api/user/<user_id>` - Get user progress

## Browser Compatibility

For speech recognition to work, use:
- Chrome (recommended)
- Edge
- Safari

Firefox has limited support for Web Speech API.

## License

MIT License
