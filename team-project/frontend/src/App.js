import React, { useState, useEffect } from 'react';


// API Base URL
const API_BASE = 'http://localhost:5000/api';

// Speech Recognition setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

// TTS Function
const speak = (text, lang = 'en') => {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'bodo' ? 'bn-IN' : lang === 'dogri' ? 'hi-IN' : 'en-US';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }
};

// Browser detection utility
const getBrowserInfo = () => {
  const ua = navigator.userAgent;
  let name = 'Unknown Browser';
  let version = 'Unknown Version';

  if (ua.includes('Chrome') && !ua.includes('Edg')) {
    name = 'Google Chrome';
    const match = ua.match(/Chrome\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  } else if (ua.includes('Firefox')) {
    name = 'Mozilla Firefox';
    const match = ua.match(/Firefox\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  } else if (ua.includes('Safari') && !ua.includes('Chrome')) {
    name = 'Safari';
    const match = ua.match(/Version\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  } else if (ua.includes('Edg')) {
    name = 'Microsoft Edge';
    const match = ua.match(/Edg\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  } else if (ua.includes('Opera') || ua.includes('OPR')) {
    name = 'Opera';
    const match = ua.match(/(?:Opera|OPR)\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  }

  return { name, version };
};

// Error logging utility
const logSpeechErrorToBackend = async (errorType, errorMessage, language) => {
  try {
    await fetch(`${API_BASE}/log-speech-error`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error_type: errorType,
        error_message: errorMessage,
        language: language
      })
    });
  } catch (e) {
    console.warn('Failed to log error to backend:', e);
  }
};

// Start Screen Component
function StartScreen({ onStart }) {
  return (
    <div className="start-screen">
      <div className="start-icon">🌐</div>
      <h1 className="start-title">AI Language Learning Game</h1>
      <p className="start-subtitle">
        Learn Bodo, Mizo, and Dogri through interactive voice-based lessons
      </p>
      
      <div className="start-features">
        <div className="feature-item">
          <div className="feature-icon">🎯</div>
          <div className="feature-name">Voice Learning</div>
          <div className="feature-description">Listen and practice speaking</div>
        </div>
        <div className="feature-item">
          <div className="feature-icon">🤖</div>
          <div className="feature-name">AI Evaluation</div>
          <div className="feature-description">Get instant pronunciation feedback</div>
        </div>
        <div className="feature-item">
          <div className="feature-icon">🏆</div>
          <div className="feature-name">Gamification</div>
          <div className="feature-description">Earn badges and level up</div>
        </div>
        <div className="feature-item">
          <div className="feature-icon">📚</div>
          <div className="feature-name">3 Languages</div>
          <div className="feature-description">Bodo, Mizo, and Dogri</div>
        </div>
      </div>

      <button className="btn btn-primary" onClick={onStart}>
        🚀 Start Learning
      </button>
    </div>
  );
}

// Language Selection Component
function LanguageSelection({ onSelect }) {
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/languages`)
      .then(res => res.json())
      .then(data => {
        setLanguages(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching languages:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div>
      <div className="page-title">
        <h2>Choose Your Language</h2>
        <p>Select a language to start learning</p>
      </div>
      <div className="language-grid">
        {languages.map(lang => (
          <div 
            key={lang.id} 
            className="language-card"
            onClick={() => onSelect(lang.id)}
          >
            <div className="language-flag">{lang.flag}</div>
            <div className="language-name">{lang.name}</div>
            <div className="language-native">{lang.native_name}</div>
            <div className="language-description">{lang.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Level Selection Component
function LevelSelection({ language, onSelect, onBack }) {
  const [levels, setLevels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/levels/${language}`)
      .then(res => res.json())
      .then(data => {
        setLevels(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching levels:', err);
        setLoading(false);
      });
  }, [language]);

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  const levelIcons = {
    beginner: '🌱',
    intermediate: '🌿'
  };

  return (
    <div>
      <div className="navigation">
        <button className="nav-btn back" onClick={onBack}>← Back</button>
      </div>
      <div className="page-title">
        <h2>Select Level</h2>
        <p>Choose your difficulty level</p>
      </div>
      <div className="level-grid">
        {levels.map(level => (
          <div 
            key={level.id} 
            className="level-card"
            onClick={() => onSelect(level.id)}
          >
            <div className="level-icon">{levelIcons[level.id]}</div>
            <div className="level-name">{level.name}</div>
            <div className="level-description">{level.description}</div>
            <div className="level-phrases">{level.phrases_count} phrases</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Game Component - FIXED VERSION
function Game({ language, level, onBack, updateScore, onGameComplete }) {
  const [phrases, setPhrases] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [userSpeech, setUserSpeech] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [gameStarted, setGameStarted] = useState(false);
  const [error, setError] = useState(null);
  const [gameCompleted, setGameCompleted] = useState(false);
  const [useTextInput, setUseTextInput] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [sessionScore, setSessionScore] = useState(0);
  const [phrasesCompleted, setPhrasesCompleted] = useState(0);

  useEffect(() => {
    fetch(`${API_BASE}/phrases/${language}/${level}`)
      .then(res => res.json())
      .then(data => {
        setPhrases(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching phrases:', err);
        setLoading(false);
      });
  }, [language, level]);

  const currentPhrase = phrases[currentIndex];

  const handleTextSubmit = () => {
    if (textInput.trim()) {
      setUserSpeech(textInput.trim());
      evaluatePronunciation(textInput.trim());
      setTextInput('');
      setUseTextInput(false);
    } else {
      setError('Please enter some text.');
    }
  };

  const handleListen = () => {
    if (currentPhrase) {
      speak(currentPhrase.phrase, language);
    }
  };

  const handleRecord = async () => {
    // Enhanced browser compatibility check
    if (!recognition) {
      const browserInfo = getBrowserInfo();
      setError(`Speech recognition is not supported in ${browserInfo.name}. You can type your answer instead.`);
      setUseTextInput(true);
      return;
    }

    // Check microphone permission
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'microphone' });
      if (permissionStatus.state === 'denied') {
        setError('Microphone permission is denied. Please enable microphone access in your browser settings and refresh the page.');
        return;
      }
    } catch (e) {
      // Permissions API not supported, try getUserMedia as fallback
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop()); // Stop immediately
      } catch (mediaError) {
        if (mediaError.name === 'NotAllowedError') {
          setError('Microphone permission denied. Please allow microphone access when prompted.');
        } else if (mediaError.name === 'NotFoundError') {
          setError('No microphone found. Please connect a microphone and try again.');
        } else {
          setError('Microphone access error. Please check your microphone settings.');
        }
        return;
      }
    }

    setIsRecording(true);
    setUserSpeech('');
    setResult(null);
    setError(null);

    // Set language based on selected language with fallbacks
    const langMap = {
      'bodo': ['bn-IN', 'bn-BD', 'hi-IN'], // Bengali variants
      'mizo': ['en-IN', 'en-US'], // English variants
      'dogri': ['hi-IN', 'pa-IN', 'en-IN'] // Hindi/Punjabi variants
    };
    
    const supportedLangs = langMap[language] || ['en-US'];
    let selectedLang = 'en-US';
    for (const lang of supportedLangs) {
      try {
        // Test if language is supported (some browsers throw error for unsupported langs)
        recognition.lang = lang;
        selectedLang = lang;
        break;
      } catch (e) {
        console.warn(`Language ${lang} not supported, trying next...`);
      }
    }
    recognition.lang = selectedLang;
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    // Clear previous event handlers
    recognition.onresult = null;
    recognition.onerror = null;
    recognition.onend = null;
    recognition.onstart = null;

    let recognitionTimeout;

    // Handle successful recognition
    const handleResult = (event) => {
      clearTimeout(recognitionTimeout);
      const results = event.results;
      if (results && results.length > 0) {
        const lastResult = results[results.length - 1];
        if (lastResult.isFinal) {
          const transcript = lastResult[0].transcript.trim();
          if (transcript) {
            console.log('Recognized:', transcript);
            setUserSpeech(transcript);
            try {
              recognition.stop();
            } catch (e) {
              console.log('Already stopped');
            }
            evaluatePronunciation(transcript);
          } else {
            setError('No speech detected. Please speak clearly and try again.');
            setIsRecording(false);
          }
        }
      }
    };

    // Enhanced error handling
    const handleError = (event) => {
      clearTimeout(recognitionTimeout);
      console.error('Speech recognition error:', event.error, event);
      setIsRecording(false);
      
      let errorMsg = 'Speech recognition failed.';
      switch (event.error) {
        case 'no-speech':
          errorMsg = 'No speech detected. Please speak clearly into your microphone.';
          break;
        case 'audio-capture':
          errorMsg = 'Microphone not accessible. Please check your microphone connection.';
          break;
        case 'not-allowed':
          errorMsg = 'Microphone permission denied. Please allow microphone access and try again.';
          break;
        case 'network':
          errorMsg = 'Network error during recognition. Please check your internet connection.';
          break;
        case 'aborted':
          errorMsg = 'Recognition was cancelled. Please try again.';
          break;
        case 'service-not-allowed':
          errorMsg = 'Speech recognition service unavailable. Please try again later.';
          break;
        case 'bad-grammar':
          errorMsg = 'Speech recognition configuration error. Please refresh the page.';
          break;
        case 'language-not-supported':
          errorMsg = `Language ${recognition.lang} is not supported. Using English fallback.`;
          recognition.lang = 'en-US';
          // Could retry here, but for simplicity, just inform user
          break;
        default:
          errorMsg = `Recognition error: ${event.error}. Please try again.`;
      }

      // Log error to backend for analytics
      logSpeechErrorToBackend(event.error, errorMsg, language);

      setError(errorMsg);
    };

    // Handle recognition start
    const handleStart = () => {
      console.log('Recognition started');
      // Set a timeout to stop recognition if it doesn't end naturally
      recognitionTimeout = setTimeout(() => {
        console.log('Recognition timeout, stopping...');
        try {
          recognition.stop();
        } catch (e) {
          console.log('Failed to stop recognition on timeout');
        }
        setError('Recognition timed out. Please try again.');
        setIsRecording(false);
      }, 10000); // 10 second timeout
    };

    // Handle end of recognition
    const handleEnd = () => {
      clearTimeout(recognitionTimeout);
      console.log('Recognition ended');
      setIsRecording(false);
      // Clean up handlers
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
      recognition.onstart = null;
    };

    // Assign handlers
    recognition.onresult = handleResult;
    recognition.onerror = handleError;
    recognition.onend = handleEnd;
    recognition.onstart = handleStart;

    // Start recognition with enhanced error handling
    try {
      recognition.start();
    } catch (err) {
      console.error('Failed to start recognition:', err);
      setIsRecording(false);
      if (err.name === 'InvalidStateError') {
        setError('Recognition is already running. Please wait for it to finish.');
      } else if (err.name === 'NotAllowedError') {
        setError('Microphone permission denied. Please allow access and try again.');
      } else {
        setError(`Failed to start recognition: ${err.message}. Please try again.`);
      }
    }
  };

  const evaluatePronunciation = async (speech) => {
    try {
      const response = await fetch(`${API_BASE}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          language,
          phrase_id: currentPhrase.id,
          user_speech: speech
        })
      });
      const data = await response.json();
      setResult(data);
      updateScore(data.score);
      
      // Update session stats
      setSessionScore(prev => prev + data.score);
      setPhrasesCompleted(prev => prev + 1);
      
      // Auto-progress after 2 seconds
      setTimeout(() => {
        handleNext();
      }, 2000);
    } catch (err) {
      console.error('Evaluation error:', err);
      setError('Failed to evaluate. Please try again.');
    }
  };

  const handleNext = () => {
    if (currentIndex < phrases.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setResult(null);
      setUserSpeech('');
      setError(null);
    } else {
      // Game completed!
      setGameCompleted(true);
      if (onGameComplete) {
        onGameComplete({
          totalPhrases: phrases.length,
          score: sessionScore,
          language,
          level
        });
      }
    }
  };

  const handleStart = () => {
    setGameStarted(true);
    setCurrentIndex(0);
    setSessionScore(0);
    setPhrasesCompleted(0);
    setResult(null);
    setUserSpeech('');
    setError(null);
    if (currentPhrase) {
      setTimeout(() => speak(currentPhrase.phrase, language), 500);
    }
  };

  const handlePlayAgain = () => {
    setGameCompleted(false);
    setCurrentIndex(0);
    setSessionScore(0);
    setPhrasesCompleted(0);
    setResult(null);
    setUserSpeech('');
    setError(null);
    if (currentPhrase) {
      setTimeout(() => speak(currentPhrase.phrase, language), 500);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  // Game Completed Screen
  if (gameCompleted) {
    const avgScore = phrasesCompleted > 0 ? Math.round(sessionScore / phrasesCompleted) : 0;
    return (
      <div className="game-container">
        <div className="phrase-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎉</div>
          <h2>Congratulations!</h2>
          <p style={{ margin: '1rem 0', color: '#636e72' }}>
            You've completed all {phrases.length} phrases in this level!
          </p>
          
          <div style={{ 
            background: '#f8f9fa', 
            borderRadius: '12px', 
            padding: '1.5rem',
            margin: '1.5rem 0'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-around' }}>
              <div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#6c5ce7' }}>
                  {sessionScore}
                </div>
                <div style={{ color: '#636e72' }}>Total Points</div>
              </div>
              <div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#00b894' }}>
                  {avgScore}%
                </div>
                <div style={{ color: '#636e72' }}>Average Score</div>
              </div>
              <div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fdcb6e' }}>
                  {phrasesCompleted}
                </div>
                <div style={{ color: '#636e72' }}>Phrases</div>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn btn-primary" onClick={handlePlayAgain}>
              🔄 Play Again
            </button>
            <button className="btn btn-secondary" onClick={onBack}>
              ← Back to Levels
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!gameStarted) {
    return (
      <div className="game-container">
        <div className="navigation">
          <button className="nav-btn back" onClick={onBack}>← Back</button>
        </div>
        <div className="phrase-card">
          <h2>Ready to Start?</h2>
          <p style={{ margin: '1rem 0', color: '#636e72' }}>
            You will hear a phrase in {language}. Listen carefully, then try to repeat it.
            The AI will evaluate your pronunciation!
          </p>
          <p style={{ marginBottom: '1.5rem', color: '#636e72' }}>
            Total phrases: {phrases.length}
          </p>
          <button className="btn btn-primary" onClick={handleStart}>
            🎮 Start Game
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      <div className="game-header">
        <button className="btn btn-secondary" onClick={onBack}>← Exit</button>
        <div className="game-progress">
          <span>Phrase {currentIndex + 1} of {phrases.length}</span>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${((currentIndex + 1) / phrases.length) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="phrase-card">
        <div className="phrase-number">Phrase {currentIndex + 1}</div>
        <div className="phrase-text">{currentPhrase?.phrase}</div>
        <div className="phrase-meaning">{currentPhrase?.meaning}</div>
        <div className="phrase-phonetic">{currentPhrase?.phonetic}</div>

        {isRecording && (
          <div className="recording-indicator">
            <div className="recording-dot"></div>
            <span>Listening...</span>
          </div>
        )}

        {error && (
          <div style={{ 
            background: '#fee', 
            border: '1px solid #f88', 
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '1rem',
            color: '#c00'
          }}>
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        {userSpeech && !result && !error && (
          <div className="user-speech">
            <div className="user-speech-label">You said:</div>
            <div className="user-speech-text">{userSpeech}</div>
          </div>
        )}

        {result && (
          <div className="result-card">
            <div className="result-emoji">{result.emoji}</div>
            <div className={`result-score ${result.score >= 90 ? 'excellent' : result.score >= 70 ? 'good' : 'needs-work'}`}>
              {result.score}%
            </div>
            <div className="result-feedback">{result.feedback}</div>
            <div className="result-details">
              <div className="result-row">
                <span className="result-label">Original:</span>
                <span className="result-value">{result.original_phrase}</span>
              </div>
              <div className="result-row">
                <span className="result-label">You said:</span>
                <span className="result-value">{result.user_speech}</span>
              </div>
            </div>
          </div>
        )}

        <div className="action-buttons">
          <button className="btn btn-primary" onClick={handleListen} disabled={isRecording}>
            🔊 Listen
          </button>
          
          {useTextInput ? (
            <div className="text-input-section">
              <input
                type="text"
                className="text-input"
                placeholder="Type what you heard..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
              />
              <button 
                className="btn btn-success" 
                onClick={handleTextSubmit}
                disabled={!textInput.trim()}
              >
                ✅ Submit
              </button>
            </div>
          ) : (
            <button 
              className={`btn ${result ? 'btn-success' : 'btn-primary'}`} 
              onClick={result ? handleNext : handleRecord}
              disabled={isRecording}
            >
              {result ? '➡️ Next...' : '🎤 Speak Now'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// Progress Component
function Progress({ userId, onBack }) {
  const [user, setUser] = useState(null);
  const [badges, setBadges] = useState({});

  useEffect(() => {
    fetch(`${API_BASE}/user/${userId}`)
      .then(res => res.json())
      .then(data => setUser(data))
      .catch(err => console.error('Error fetching user:', err));

    fetch(`${API_BASE}/badges`)
      .then(res => res.json())
      .then(data => setBadges(data))
      .catch(err => console.error('Error fetching badges:', err));
  }, [userId]);

  if (!user) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div className="progress-container">
      <div className="navigation">
        <button className="nav-btn back" onClick={onBack}>← Back</button>
      </div>
      
      <div className="page-title">
        <h2>Your Progress</h2>
        <p>Track your learning journey</p>
      </div>

      <div className="progress-summary">
        <div className="progress-stats">
          <div>
            <div className="stat-value">{user.total_score}</div>
            <div className="stat-label">Total Points</div>
          </div>
          <div>
            <div className="stat-value">{user.badges?.length || 0}</div>
            <div className="stat-label">Badges Earned</div>
          </div>
          <div>
            <div className="stat-value">{user.streak || 0}</div>
            <div className="stat-label">Day Streak</div>
          </div>
        </div>
      </div>

      <div className="badges-section">
        <h3 className="badges-title">🏆 Your Badges</h3>
        <div className="badges-grid">
          {user.badges?.map(badgeId => (
            badges[badgeId] && (
              <div key={badgeId} className="badge-item">
                <div className="badge-icon">{badges[badgeId].icon}</div>
                <div className="badge-name">{badges[badgeId].name}</div>
                <div className="badge-description">{badges[badgeId].description}</div>
              </div>
            )
          ))}
          {(!user.badges || user.badges.length === 0) && (
            <p style={{ gridColumn: '1 / -1', textAlign: 'center', color: '#636e72' }}>
              Complete lessons to earn badges! 🎯
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  const [screen, setScreen] = useState('start');
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  const [selectedLevel, setSelectedLevel] = useState(null);
  const [totalScore, setTotalScore] = useState(0);
  const userId = 'user_1';

  const updateScore = (score) => {
    setTotalScore(prev => prev + score);
    fetch(`${API_BASE}/score`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        language: selectedLanguage,
        level: selectedLevel,
        score: score
      })
    });
  };

  const handleGameComplete = (results) => {
    console.log('Game completed:', results);
    // Could show a modal or navigate to results
  };

  const renderScreen = () => {
    switch (screen) {
      case 'start':
        return <StartScreen onStart={() => setScreen('language')} />;
      case 'language':
        return <LanguageSelection onSelect={(lang) => {
          setSelectedLanguage(lang);
          setScreen('level');
        }} />;
      case 'level':
        return (
          <LevelSelection 
            language={selectedLanguage}
            onSelect={(level) => {
              setSelectedLevel(level);
              setScreen('game');
            }}
            onBack={() => setScreen('language')}
          />
        );
      case 'game':
        return (
          <Game 
            language={selectedLanguage}
            level={selectedLevel}
            onBack={() => setScreen('level')}
            updateScore={updateScore}
            onGameComplete={handleGameComplete}
          />
        );
      case 'progress':
        return <Progress userId={userId} onBack={() => setScreen('start')} />;
      default:
        return <StartScreen onStart={() => setScreen('language')} />;
    }
  };

  return (
    <div className="app">
      {screen !== 'start' && screen !== 'language' && screen !== 'level' && (
        <header className="header">
          <div className="logo">
            <span className="logo-icon">🌐</span>
            <h1>AI Language Learning</h1>
          </div>
          <div className="header-stats">
            <div className="stat-item">
              <span>⭐</span>
              <span>{totalScore} Points</span>
            </div>
            <div className="stat-item" onClick={() => setScreen('progress')} style={{ cursor: 'pointer' }}>
              <span>🏆</span>
              <span>Progress</span>
            </div>
          </div>
        </header>
      )}

      <main className="main-content">
        {renderScreen()}
      </main>
    </div>
  );
}

export default App;
