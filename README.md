# 🎙️ AI Voice Detection API

An intelligent REST API that detects whether a voice sample is AI-generated or spoken by a real human. Supports 5 languages: **Tamil, English, Hindi, Malayalam, and Telugu**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

## 🌟 Features

- ✅ **Multi-language Support**: Tamil, English, Hindi, Malayalam, Telugu
- ✅ **High Accuracy**: Advanced audio feature analysis
- ✅ **Secure API**: API key authentication
- ✅ **RESTful Design**: Standard JSON request/response
- ✅ **Docker Ready**: Easy deployment with containerization
- ✅ **Real-time Processing**: Fast voice classification
- ✅ **Confidence Scoring**: Returns 0.0-1.0 confidence scores
- ✅ **Detailed Explanations**: Provides reasoning for classification

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker (optional, but recommended)

### Installation

#### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/voice-detection-api.git
cd voice-detection-api

# Build and run with Docker Compose
docker-compose up --build

# API will be available at http://localhost:8000
```

#### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/voice-detection-api.git
cd voice-detection-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r req.txt

# Run the API
python main.py

# API will be available at http://localhost:8000
```

## 📡 API Documentation

### Base URL

```
http://localhost:8000  (for local development)
https://your-deployment-url.com  (for production)
```

### Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### 2. Root Endpoint

```http
GET /
```

**Response:**
```json
{
  "service": "AI Voice Detection API",
  "status": "running",
  "version": "1.0.0",
  "supported_languages": ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]
}
```

#### 3. Voice Detection (Main Endpoint)

```http
POST /api/voice-detection
```

**Headers:**
```
Content-Type: application/json
x-api-key: sk_test_123456789
```

**Request Body:**
```json
{
  "language": "English",
  "audioFormat": "mp3",
  "audioBase64": "BASE64_ENCODED_AUDIO_DATA"
}
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "language": "English",
  "classification": "AI_GENERATED",
  "confidenceScore": 0.85,
  "explanation": "Detected highly consistent pitch, uniform spectral characteristics suggesting synthetic generation"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "status": "error",
  "message": "Invalid API key"
}
```

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Invalid base64 encoding"
}
```

## 🔑 Authentication

All requests to `/api/voice-detection` must include an API key in the header:

```
x-api-key: sk_test_123456789
```

**To change the API key**, edit the `main.py` file:

```python
VALID_API_KEY = "your_new_api_key_here"
```

Or set it as an environment variable:

```bash
export API_KEY="your_new_api_key_here"
```

## 🧪 Testing

### Using the Test Script

```bash
# Test with an audio file
python test_api.py sample.mp3 English

# This will:
# 1. Encode your audio to base64
# 2. Send it to the API
# 3. Display the results
```

### Using curl

```bash
# First, encode your audio file
python encode_audio.py sample.mp3 English

# This generates test_payload.json
# Then use curl:
curl -X POST http://localhost:8000/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_test_123456789" \
  -d @test_payload.json
```

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with invalid API key (should return 401)
curl -X POST http://localhost:8000/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: wrong_key" \
  -d '{"language":"English","audioFormat":"mp3","audioBase64":"test"}'
```

## 🎯 How It Works

The API uses advanced audio signal processing to detect AI-generated voices by analyzing:

### 1. **Pitch Analysis**
- AI voices often have unnaturally consistent pitch
- Measures pitch variability and range
- Low variability indicates synthetic generation

### 2. **Spectral Features**
- Analyzes frequency distribution
- AI voices show more uniform spectral characteristics
- Checks spectral centroid, rolloff, and bandwidth

### 3. **MFCC (Mel-Frequency Cepstral Coefficients)**
- Captures vocal tract characteristics
- AI voices have distinct MFCC patterns
- Analyzes 20 MFCC coefficients and their variations

### 4. **Energy Patterns**
- Measures audio energy consistency
- AI voices maintain very consistent energy levels
- Human voices have natural energy fluctuations

### 5. **Harmonic Structure**
- Analyzes harmonic vs. percussive components
- AI voices have artificial harmonic ratios
- Detects synthetic audio generation patterns

### 6. **Statistical Properties**
- Signal distribution analysis (skewness, kurtosis)
- Zero-crossing rate patterns
- Temporal consistency metrics

### Classification Logic

```python
if confidence_score >= 0.50:
    classification = "AI_GENERATED"
else:
    classification = "HUMAN"
```

## 🌍 Supported Languages

- 🇮🇳 **Tamil** (தமிழ்)
- 🇬🇧 **English**
- 🇮🇳 **Hindi** (हिन्दी)
- 🇮🇳 **Malayalam** (മലയാളം)
- 🇮🇳 **Telugu** (తెలుగు)

## 📁 Project Structure

```
voice-detection-api/
│
├── main.py                 # Main FastAPI application
├── req.txt                 # Python dependencies
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Docker Compose setup
├── render.yaml             # Render.com deployment config
├── railway.json            # Railway.app deployment config
│
├── test_api.py             # API testing script
├── encode_audio.py         # Audio encoding utility
├── monitor_api.py          # API monitoring tool
│
└── README.md               # This file
```

## 🚢 Deployment

### Deploy to Render.com (FREE)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/voice-detection-api.git
   git push -u origin main
   ```

2. **Go to [Render.com](https://render.com)**
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Environment**: Docker
   - **Plan**: Free
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. Your API URL: `https://your-app.onrender.com`

### Deploy to Railway.app (FREE)

1. Push code to GitHub (see above)
2. Go to [Railway.app](https://railway.app)
3. **New Project** → **Deploy from GitHub**
4. Select your repository
5. Railway auto-detects Docker
6. **Generate Domain** in Settings
7. Done!

### Deploy to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch
fly deploy
```

### Deploy to Google Cloud Run

```bash
gcloud run deploy voice-detection-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Example Usage

### Python Example

```python
import requests
import base64

# Read audio file
with open("sample.mp3", "rb") as f:
    audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

# Prepare request
url = "https://your-api-url.com/api/voice-detection"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "sk_test_123456789"
}
payload = {
    "language": "English",
    "audioFormat": "mp3",
    "audioBase64": audio_base64
}

# Send request
response = requests.post(url, headers=headers, json=payload)
result = response.json()

print(f"Classification: {result['classification']}")
print(f"Confidence: {result['confidenceScore']}")
print(f"Explanation: {result['explanation']}")
```

### JavaScript Example

```javascript
const fs = require('fs');
const axios = require('axios');

// Read and encode audio
const audioBuffer = fs.readFileSync('sample.mp3');
const audioBase64 = audioBuffer.toString('base64');

// Send request
const response = await axios.post(
  'https://your-api-url.com/api/voice-detection',
  {
    language: 'English',
    audioFormat: 'mp3',
    audioBase64: audioBase64
  },
  {
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': 'sk_test_123456789'
    }
  }
);

console.log(response.data);
```

### curl Example

```bash
# Encode audio
BASE64_AUDIO=$(base64 -w 0 sample.mp3)

# Send request
curl -X POST https://your-api-url.com/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_test_123456789" \
  -d "{
    \"language\": \"English\",
    \"audioFormat\": \"mp3\",
    \"audioBase64\": \"$BASE64_AUDIO\"
  }"
```

## 🔧 Configuration

### Environment Variables

```bash
# API Key (optional - defaults to sk_test_123456789)
export API_KEY="your_custom_api_key"

# Port (optional - defaults to 8000)
export PORT=8000
```

### Docker Environment Variables

In `docker-compose.yml`:

```yaml
services:
  api:
    environment:
      - API_KEY=your_custom_api_key
      - PORT=8000
```

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install -r req.txt
```

### Issue: "Invalid API key"

**Solution:**
- Check that `x-api-key` header is set correctly
- Verify the API key matches the one in `main.py`

### Issue: "Invalid base64 encoding"

**Solution:**
- Ensure audio is properly base64 encoded
- Use `encode_audio.py` to encode your audio files
- Check that the entire base64 string is included

### Issue: Slow processing

**Solution:**
- Audio processing is CPU-intensive
- Consider upgrading server resources
- Reduce audio file size/quality if possible

### Issue: Docker build fails

**Solution:**
```bash
# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```

## 📈 Performance

- **Average Response Time**: 2-5 seconds per request
- **Supported Audio Length**: Up to 60 seconds recommended
- **Max File Size**: 5MB (base64 encoded)
- **Concurrent Requests**: Depends on deployment resources

## 🛡️ Security

- ✅ API key authentication required
- ✅ No data persistence (audio is not stored)
- ✅ Input validation on all requests
- ✅ Rate limiting recommended for production
- ✅ HTTPS enforced on deployment platforms

## 📝 API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Voice analyzed successfully |
| 400 | Bad Request - Invalid input format |
| 401 | Unauthorized - Invalid/missing API key |
| 500 | Internal Server Error - Processing error |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Created for AI Voice Detection Hackathon

## 🙏 Acknowledgments

- FastAPI framework for the API structure
- Librosa library for audio processing
- scikit-learn for feature analysis
- Docker for containerization

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review the API documentation

## 🎯 Hackathon Submission

**API Endpoint**: `https://your-deployment-url.com/api/voice-detection`  
**API Key**: `sk_test_123456789`

### Testing the Submission

```bash
# Health check
curl https://your-deployment-url.com/health

# Voice detection test
curl -X POST https://your-deployment-url.com/api/voice-detection \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_test_123456789" \
  -d @test_payload.json
```

## 📊 Technical Specifications

- **Framework**: FastAPI 0.115.0
- **Python Version**: 3.11+
- **Audio Processing**: Librosa 0.10.2
- **Containerization**: Docker
- **Deployment**: Render.com / Railway.app / Fly.io / Google Cloud Run

## 🚀 Future Improvements

- [ ] Machine learning model integration
- [ ] Support for more audio formats (WAV, FLAC)
- [ ] Batch processing support
- [ ] WebSocket for real-time streaming
- [ ] Database integration for analytics
- [ ] Admin dashboard
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Multi-region deployment

---

**Made with ❤️ for the AI Voice Detection Hackathon**

⭐ **Star this repository if you find it useful!**
