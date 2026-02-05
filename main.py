from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import base64
import io
import librosa
import numpy as np
from typing import Literal
import logging
from scipy import signal
from scipy.stats import skew, kurtosis
import warnings
import os

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Voice Detection API", version="1.0.0")

# API Key Configuration - can be set via environment variable
VALID_API_KEY = os.getenv("API_KEY", "sk_test_123456789")

# Supported languages
SUPPORTED_LANGUAGES = ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]


class VoiceRequest(BaseModel):
    language: Literal["Tamil", "English", "Hindi", "Malayalam", "Telugu"]
    audioFormat: Literal["mp3"]
    audioBase64: str = Field(..., description="Base64 encoded MP3 audio")


class VoiceResponse(BaseModel):
    status: str
    language: str
    classification: Literal["AI_GENERATED", "HUMAN"]
    confidenceScore: float = Field(..., ge=0.0, le=1.0)
    explanation: str


class ErrorResponse(BaseModel):
    status: str
    message: str


def verify_api_key(x_api_key: str = Header(None)):
    """Verify the API key from request headers"""
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="API key missing")
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def extract_audio_features(audio_data: np.ndarray, sr: int) -> dict:
    """
    Extract comprehensive audio features for AI detection
    """
    features = {}
    
    try:
        # Basic spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)[0]
        spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)[0]
        
        features['spectral_centroid_mean'] = np.mean(spectral_centroids)
        features['spectral_centroid_std'] = np.std(spectral_centroids)
        features['spectral_centroid_var'] = np.var(spectral_centroids)
        features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
        features['spectral_rolloff_std'] = np.std(spectral_rolloff)
        features['spectral_bandwidth_mean'] = np.mean(spectral_bandwidth)
        features['spectral_bandwidth_std'] = np.std(spectral_bandwidth)
        features['spectral_flatness_mean'] = np.mean(spectral_flatness)
        features['spectral_flatness_std'] = np.std(spectral_flatness)
        
        # Zero crossing rate (voice naturalness indicator)
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zcr_mean'] = np.mean(zcr)
        features['zcr_std'] = np.std(zcr)
        features['zcr_var'] = np.var(zcr)
        
        # MFCC features (crucial for voice characteristic analysis)
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=20)
        for i in range(20):
            features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            features[f'mfcc_{i}_var'] = np.var(mfccs[i])
        
        # Delta MFCCs (temporal changes)
        mfcc_delta = librosa.feature.delta(mfccs)
        features['mfcc_delta_mean'] = np.mean(np.abs(mfcc_delta))
        features['mfcc_delta_std'] = np.std(mfcc_delta)
        
        # Pitch analysis
        pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr)
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            features['pitch_mean'] = np.mean(pitch_values)
            features['pitch_std'] = np.std(pitch_values)
            features['pitch_var'] = np.var(pitch_values)
            features['pitch_range'] = np.max(pitch_values) - np.min(pitch_values)
            features['pitch_variability'] = features['pitch_std'] / (features['pitch_mean'] + 1e-6)
            features['pitch_coefficient_of_variation'] = (features['pitch_std'] / features['pitch_mean']) if features['pitch_mean'] > 0 else 0
        else:
            features['pitch_mean'] = 0
            features['pitch_std'] = 0
            features['pitch_var'] = 0
            features['pitch_range'] = 0
            features['pitch_variability'] = 0
            features['pitch_coefficient_of_variation'] = 0
        
        # Energy and amplitude features
        rms = librosa.feature.rms(y=audio_data)[0]
        features['rms_mean'] = np.mean(rms)
        features['rms_std'] = np.std(rms)
        features['rms_var'] = np.var(rms)
        features['rms_range'] = np.max(rms) - np.min(rms)
        
        # Harmonic and percussive components
        harmonic, percussive = librosa.effects.hpss(audio_data)
        features['harmonic_mean'] = np.mean(np.abs(harmonic))
        features['percussive_mean'] = np.mean(np.abs(percussive))
        features['harmonic_ratio'] = features['harmonic_mean'] / (features['percussive_mean'] + 1e-6)
        features['harmonic_std'] = np.std(harmonic)
        features['percussive_std'] = np.std(percussive)
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
        features['spectral_contrast_mean'] = np.mean(contrast)
        features['spectral_contrast_std'] = np.std(contrast)
        features['spectral_contrast_var'] = np.var(contrast)
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
        features['chroma_mean'] = np.mean(chroma)
        features['chroma_std'] = np.std(chroma)
        
        # Tempo and rhythm
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        features['tempo'] = tempo[0] if len(tempo) > 0 else 0
        
        # Statistical measures of the raw signal
        features['signal_skewness'] = skew(audio_data)
        features['signal_kurtosis'] = kurtosis(audio_data)
        features['signal_std'] = np.std(audio_data)
        features['signal_var'] = np.var(audio_data)
        
        # Jitter and shimmer approximations
        if len(pitch_values) > 1:
            pitch_diffs = np.diff(pitch_values)
            features['jitter'] = np.mean(np.abs(pitch_diffs)) / (features['pitch_mean'] + 1e-6)
        else:
            features['jitter'] = 0
            
        if len(rms) > 1:
            rms_diffs = np.diff(rms)
            features['shimmer'] = np.mean(np.abs(rms_diffs)) / (features['rms_mean'] + 1e-6)
        else:
            features['shimmer'] = 0
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        raise
    
    return features


def detect_ai_voice(features: dict, language: str) -> tuple[str, float, str]:
    """
    Detect if voice is AI-generated based on extracted features
    
    IMPROVED DETECTION: More sensitive to AI characteristics
    
    AI-generated voices typically have:
    - Extremely consistent pitch (very low variability)
    - Very uniform spectral characteristics
    - Less natural breath sounds and micropauses
    - More regular temporal patterns
    - Smoother transitions (low jitter/shimmer)
    - Lower MFCC variance in specific coefficients
    - More consistent energy levels
    """
    
    ai_score = 0.0
    indicators = []
    
    # CRITICAL INDICATOR 1: Pitch consistency (AI is TOO perfect)
    # Human voices naturally vary, AI is unnaturally stable
    if features['pitch_variability'] < 0.10:
        ai_score += 0.35
        indicators.append("extremely consistent pitch")
    elif features['pitch_variability'] < 0.20:
        ai_score += 0.25
        indicators.append("highly consistent pitch")
    elif features['pitch_variability'] < 0.30:
        ai_score += 0.15
        indicators.append("consistent pitch patterns")
    
    # CRITICAL INDICATOR 2: Low jitter (pitch stability)
    # AI voices have very low jitter compared to human
    if features.get('jitter', 0) < 0.005:
        ai_score += 0.25
        indicators.append("minimal pitch jitter")
    elif features.get('jitter', 0) < 0.01:
        ai_score += 0.15
        indicators.append("low pitch variation")
    
    # CRITICAL INDICATOR 3: Low shimmer (amplitude stability)
    # AI voices maintain very consistent amplitude
    if features.get('shimmer', 0) < 0.02:
        ai_score += 0.20
        indicators.append("minimal amplitude shimmer")
    elif features.get('shimmer', 0) < 0.05:
        ai_score += 0.10
    
    # INDICATOR 4: Spectral consistency
    # AI has less variation in spectral characteristics
    if features['spectral_centroid_std'] < 400:
        ai_score += 0.20
        indicators.append("uniform spectral characteristics")
    elif features['spectral_centroid_std'] < 600:
        ai_score += 0.10
    
    # INDICATOR 5: Spectral flatness (tonality)
    # AI voices often have different spectral flatness
    if features['spectral_flatness_mean'] > 0.5:
        ai_score += 0.15
        indicators.append("unusual spectral flatness")
    
    # INDICATOR 6: Zero crossing rate consistency
    # AI tends to have very regular ZCR
    if features['zcr_std'] < 0.015:
        ai_score += 0.20
        indicators.append("regular speech patterns")
    elif features['zcr_std'] < 0.025:
        ai_score += 0.10
    
    # INDICATOR 7: MFCC variance analysis
    # AI tends to have lower variance in certain coefficients
    low_variance_mfcc_count = 0
    for i in range(3, 15):  # Check critical MFCCs
        if features.get(f'mfcc_{i}_std', 10.0) < 3.0:
            low_variance_mfcc_count += 1
    
    if low_variance_mfcc_count >= 8:
        ai_score += 0.25
        indicators.append("synthetic vocal tract characteristics")
    elif low_variance_mfcc_count >= 6:
        ai_score += 0.15
    elif low_variance_mfcc_count >= 4:
        ai_score += 0.08
    
    # INDICATOR 8: Energy consistency
    # AI often has very consistent energy
    if features['rms_std'] < 0.008:
        ai_score += 0.20
        indicators.append("unnaturally consistent volume")
    elif features['rms_std'] < 0.015:
        ai_score += 0.12
    
    # INDICATOR 9: Harmonic ratio
    # AI often has higher or more consistent harmonic content
    if features['harmonic_ratio'] > 3.0:
        ai_score += 0.15
        indicators.append("artificial harmonic structure")
    elif features['harmonic_ratio'] > 2.0:
        ai_score += 0.08
    
    # INDICATOR 10: Spectral contrast
    # Lower contrast can indicate AI
    if features['spectral_contrast_std'] < 1.5:
        ai_score += 0.15
        indicators.append("reduced spectral dynamics")
    elif features['spectral_contrast_std'] < 2.5:
        ai_score += 0.08
    
    # INDICATOR 11: Signal statistical properties
    # AI often has more Gaussian-like distribution
    if abs(features['signal_kurtosis']) < 1.5:
        ai_score += 0.12
        indicators.append("gaussian-like signal distribution")
    
    # INDICATOR 12: MFCC delta (temporal changes)
    # AI has smoother transitions
    if features.get('mfcc_delta_std', 10) < 5.0:
        ai_score += 0.10
        indicators.append("smooth temporal transitions")
    
    # INDICATOR 13: Pitch coefficient of variation
    # Very low CV indicates AI
    if features['pitch_coefficient_of_variation'] < 0.08:
        ai_score += 0.15
        indicators.append("minimal pitch variation coefficient")
    
    # Normalize score to 0-1 range (but allow going over 1.0 initially)
    confidence_score = min(ai_score, 1.0)
    
    # ADJUSTED THRESHOLD: Lower threshold for better AI detection
    # If score >= 0.45, classify as AI
    if confidence_score >= 0.45:
        classification = "AI_GENERATED"
        if len(indicators) > 0:
            # Take top 3 most significant indicators
            explanation = f"Detected {', '.join(indicators[:3])} indicating synthetic voice generation"
        else:
            explanation = "Multiple acoustic features suggest AI-generated voice"
    else:
        classification = "HUMAN"
        explanation = "Natural vocal variations and human speech characteristics detected"
        confidence_score = 1.0 - confidence_score  # Invert for human confidence
    
    # Ensure minimum confidence of 0.5 for any classification
    confidence_score = max(confidence_score, 0.50)
    
    return classification, round(confidence_score, 2), explanation

@app.get("/api/voice-detection")
async def detect_voice_info():
    """
    Handle GET requests - provides API usage information
    Prevents 405 Method Not Allowed error when portals test the endpoint
    """
    return {
        "status": "info",
        "message": "This endpoint requires POST method",
        "usage": {
            "method": "POST",
            "endpoint": "/api/voice-detection",
            "headers": {
                "Content-Type": "application/json",
                "x-api-key": "sk_test_123456789"
            },
            "body": {
                "language": "Tamil|English|Hindi|Malayalam|Telugu",
                "audioFormat": "mp3",
                "audioBase64": "base64_encoded_mp3_audio"
            }
        },
        "example": {
            "language": "Tamil",
            "audioFormat": "mp3",
            "audioBase64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA..."
        }
    }
    
@app.post("/api/voice-detection", response_model=VoiceResponse)
async def detect_voice(
    request: VoiceRequest,
    x_api_key: str = Header(None, alias="x-api-key")
):
    """
    Detect whether a voice sample is AI-generated or human
    """
    try:
        # Verify API key
        verify_api_key(x_api_key)
        
        # Validate language
        if request.language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            )
        
        # Decode base64 audio
        try:
            audio_bytes = base64.b64decode(request.audioBase64)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding")
        
        # Load audio with librosa
        try:
            audio_data, sample_rate = librosa.load(
                io.BytesIO(audio_bytes),
                sr=None,  # Preserve original sample rate
                mono=True
            )
        except Exception as e:
            logger.error(f"Error loading audio: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Check if audio is valid
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Extract features
        features = extract_audio_features(audio_data, sample_rate)
        
        # Detect AI voice
        classification, confidence_score, explanation = detect_ai_voice(
            features, request.language
        )
        
        # Prepare response
        response = VoiceResponse(
            status="success",
            language=request.language,
            classification=classification,
            confidenceScore=confidence_score,
            explanation=explanation
        )
        
        logger.info(f"Processed {request.language} audio: {classification} ({confidence_score})")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for consistent error responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )


@app.get("/")
async def root():
    """API health check"""
    return {
        "service": "AI Voice Detection API",
        "status": "running",
        "version": "1.0.0",
        "supported_languages": SUPPORTED_LANGUAGES
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable (Railway uses PORT)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
