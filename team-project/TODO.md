# Voice Detection API Implementation - TODO

## Tasks
- [ ] 1. Update requirements.txt with new dependencies (whisper, webrtcvad, pydub)
- [ ] 2. Create voice_detector.py module with VAD and speech-to-text functions
- [ ] 3. Add new API endpoints to app.py (/api/voice/detect, /api/voice/transcribe, /api/voice/analyze)
- [ ] 4. Install dependencies
- [ ] 5. Test the API

## Implementation Details

### Dependencies:
- openai-whisper - Speech-to-text (free, offline)
- webrtcvad - Voice Activity Detection
- pydub - Audio processing
- soundfile - Audio file handling

### New Endpoints:
1. POST /api/voice/detect - Voice Activity Detection
2. POST /api/voice/transcribe - Speech-to-Text
3. POST /api/voice/analyze - Complete pronunciation analysis
