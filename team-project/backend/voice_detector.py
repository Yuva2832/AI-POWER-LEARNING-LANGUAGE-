"""
Voice Detection API Module

This module provides:
- Voice Activity Detection (VAD)
- Speech-to-Text transcription using Whisper
- Audio analysis for pronunciation evaluation

Dependencies: openai-whisper, webrtcvad, pydub, soundfile, numpy
"""

import io
import numpy as np
import tempfile
import os
import base64


class SimpleEnergyBasedVAD:
    """
    Energy-based Voice Activity Detector
    
    Uses root mean square (RMS) energy thresholding to detect speech.
    This is a simple but effective method for detecting voiced segments.
    
    Attributes:
        energy_threshold: RMS threshold below which audio is considered silence
        sample_rate: Sample rate of the audio
    """
    
    def __init__(self, energy_threshold=0.02, sample_rate=16000):
        self.energy_threshold = energy_threshold
        self.sample_rate = sample_rate
    
    def _compute_energy(self, audio_data):
        """Compute RMS energy of audio signal"""
        if isinstance(audio_data, bytes):
            try:
                # Convert bytes to int16 array
                if len(audio_data) % 2 == 0:
                    audio_int = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    return float(np.sqrt(np.mean(audio_int ** 2)))
            except Exception:
                pass
            return 0.0
        elif isinstance(audio_data, np.ndarray):
            return float(np.sqrt(np.mean(audio_data ** 2)))
        return 0.0
    
    def is_speech(self, audio_frame):
        """
        Check if audio frame contains speech based on energy threshold
        
        Args:
            audio_frame: bytes or numpy array of audio data
            
        Returns:
            bool: True if speech detected in frame
        """
        energy = self._compute_energy(audio_frame)
        return energy > self.energy_threshold


# Singleton VAD instance
_vad_instance = None

def get_vad():
    """Get or create the VAD singleton instance"""
    global _vad_instance
    if _vad_instance is None:
        _vad_instance = SimpleEnergyBasedVAD()
    return _vad_instance


def detect_voice_activity(audio_data, sample_rate=16000):
    """
    Detect whether audio segment contains speech
    
    Args:
        audio_data: bytes or numpy array of audio data
        sample_rate: Sample rate of the audio (default 16000)
    
    Returns:
        dict: Detection results with voice_present and confidence
    """
    vad = get_vad()
    vad.sample_rate = sample_rate
    
    if isinstance(audio_data, np.ndarray):
        # For numpy arrays, compute overall energy
        energy = vad._compute_energy(audio_data)
        voice_present = energy > vad.energy_threshold
        confidence = min(1.0, energy / (vad.energy_threshold * 5)) if voice_present else 0.0
    else:
        # For bytes
        voice_present = vad.is_speech(audio_data)
        confidence = 0.8 if voice_present else 0.0
    
    return {
        'voice_present': voice_present,
        'confidence': round(confidence, 2),
        'duration_ms': len(audio_data) // (sample_rate // 1000) if isinstance(audio_data, (bytes, np.ndarray)) else 0
    }


def transcribe_speech(audio_data, language=None):
    """
    Transcribe speech to text using Whisper
    
    Args:
        audio_data: bytes or numpy array of audio data
        language: Language code (e.g., 'hi' for Hindi, 'en' for English)
                 If None, auto-detect
    
    Returns:
        dict: Transcription results with text and confidence
    """
    try:
        import whisper
    except ImportError:
        return {
            'success': False,
            'error': 'Whisper not installed. Please install openai-whisper.',
            'text': '',
            'confidence': 0.0
        }
    
    try:
        # Load Whisper model (small model for speed, can use 'medium' or 'large' for better accuracy)
        model = whisper.load_model("base")
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_path = tmp_file.name
            
            # If audio is numpy array, save it
            if isinstance(audio_data, np.ndarray):
                import soundfile as sf
                sf.write(tmp_path, audio_data, 16000)
            else:
                # Write bytes directly
                tmp_file.write(audio_data)
        
        # Transcribe
        result = model.transcribe(tmp_path, language=language)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            'success': True,
            'text': result['text'].strip(),
            'confidence': result.get('confidence', 0.0),
            'language': result.get('language', language or 'auto-detected')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'confidence': 0.0
        }


def analyze_pronunciation(audio_data, expected_text, language=None):
    """
    Complete pronunciation analysis
    
    Combines VAD and speech-to-text to evaluate pronunciation
    
    Args:
        audio_data: bytes or numpy array of audio data
        expected_text: The text the user was expected to say
        language: Language code
    
    Returns:
        dict: Analysis results with score and feedback
    """
    # Step 1: Voice Activity Detection
    vad_result = detect_voice_activity(audio_data)
    
    if not vad_result['voice_present']:
        return {
            'success': False,
            'error': 'No speech detected in audio',
            'score': 0,
            'feedback': 'Please speak clearly into the microphone and try again.',
            'voice_detected': False
        }
    
    # Step 2: Speech-to-Text
    stt_result = transcribe_speech(audio_data, language)
    
    if not stt_result['success']:
        return {
            'success': False,
            'error': stt_result.get('error', 'Transcription failed'),
            'score': 0,
            'feedback': 'Could not process audio. Please try again with clearer audio.',
            'voice_detected': True
        }
    
    # Step 3: Compare transcribed text with expected text
    transcribed = stt_result['text'].lower().strip()
    expected = expected_text.lower().strip()
    
    # Calculate similarity score
    score = calculate_similarity(expected, transcribed)
    
    # Generate feedback
    if score >= 90:
        feedback = "Excellent! Your pronunciation is nearly perfect! 🌟"
    elif score >= 70:
        feedback = "Good job! Keep practicing to improve further! 👍"
    elif score >= 50:
        feedback = "Not bad! Try to match the pronunciation more closely. 💬"
    else:
        feedback = "Keep practicing! Listen carefully and try again. 🎯"
    
    return {
        'success': True,
        'score': score,
        'feedback': feedback,
        'transcribed_text': stt_result['text'],
        'expected_text': expected_text,
        'confidence': stt_result['confidence'],
        'voice_detected': True
    }


def calculate_similarity(original, spoken):
    """
    Calculate pronunciation similarity score
    
    Args:
        original: The expected text
        spoken: The transcribed text
    
    Returns:
        int: Similarity score (0-100)
    """
    if not spoken:
        return 0
    
    # Clean strings
    original_clean = ''.join(c.lower() for c in original if c.isalnum())
    spoken_clean = ''.join(c.lower() for c in spoken if c.isalnum())
    
    if original_clean == spoken_clean:
        return 100
    
    # Calculate character-level similarity
    common = sum(1 for c in original_clean if c in spoken_clean)
    max_len = max(len(original_clean), len(spoken_clean))
    
    if max_len == 0:
        return 0
    
    similarity = (common / max_len) * 100
    
    # Bonus for getting the start right
    if original_clean[:2] == spoken_clean[:2]:
        similarity += 10
    
    return min(100, int(similarity))


def process_audio_base64(audio_base64, sample_rate=16000):
    """
    Process base64 encoded audio data
    
    Args:
        audio_base64: Base64 encoded audio string
        sample_rate: Sample rate of the audio
    
    Returns:
        numpy array of audio data
    """
    try:
        # Decode base64
        audio_bytes = base64.b64decode(audio_base64)
        
        # Convert to numpy array (assuming 16-bit PCM)
        audio_int = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        return audio_int
    except Exception as e:
        raise ValueError(f"Failed to decode audio: {str(e)}")


# Language code mapping for Whisper
LANGUAGE_MAP = {
    'bodo': 'hi',  # Bodo uses Devanagari script, similar to Hindi
    'mizo': 'en',  # Mizo uses Latin script
    'dogri': 'hi',  # Dogri uses Devanagari script
}

def get_whisper_language(language):
    """Get Whisper language code from app language"""
    return LANGUAGE_MAP.get(language, 'en')
