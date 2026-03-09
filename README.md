# AI-Powered Language Learning Game

This repository contains an AI-powered language learning project with a Python backend and a React/React Native frontend.

## Repository Structure

- `Language_Learning_Game/` - A separate language learning game project (Python backend + Flutter mobile app files)
- `team-project/` - Main project directory containing backend and frontend code
  - `backend/` - Flask backend with APIs, database, and voice detection
  - `frontend/` - React frontend web app

## Getting Started

### Backend (Python)
1. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows PowerShell
   source venv/bin/activate       # macOS/Linux
   ```
2. Install dependencies:
   ```sh
   pip install -r team-project/backend/requirements.txt
   ```
3. Run the backend:
   ```sh
   python team-project/backend/app.py
   ```

### Frontend (React)
1. Install dependencies:
   ```sh
   cd team-project/frontend
   npm install
   ```
2. Start the development server:
   ```sh
   npm start
   ```

## Notes
- The repository includes `AI-Powered Language Learning Game.doc` as a design/documentation file.
- The backend uses SQLite by default (see `team-project/backend/language_learning.db`).

---

If you want help improving the README or organizing the repo, just ask!