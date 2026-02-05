import requests
import base64
import json
import sys

# Configuration - UPDATE THIS WITH YOUR RAILWAY URL
API_URL = "http://localhost:8000/api/voice-detection"  # Change to your Railway URL
API_KEY = "sk_test_123456789"

def test_api_with_sample(audio_file_path: str, language: str, api_url: str = None):
    """Test the API with a sample audio file"""
    
    if api_url is None:
        api_url = API_URL
    
    print(f"\n{'='*60}")
    print(f"Testing with {language} audio")
    print(f"API URL: {api_url}")
    print(f"{'='*60}")
    
    try:
        # Read and encode audio file
        with open(audio_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        print(f"✅ Audio file loaded: {len(audio_bytes)} bytes")
        print(f"✅ Base64 encoded: {len(audio_base64)} characters")
        
        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }
        
        payload = {
            "language": language,
            "audioFormat": "mp3",
            "audioBase64": audio_base64
        }
        
        print(f"\n📤 Sending request to API...")
        print(f"   (This may take 5-10 seconds for audio processing)")
        
        # Send request
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"\n📊 Results:")
            print(f"   Status: {result['status']}")
            print(f"   Language: {result['language']}")
            print(f"   Classification: {result['classification']}")
            print(f"   Confidence Score: {result['confidenceScore']}")
            print(f"   Explanation: {result['explanation']}")
            return result
        else:
            print(f"\n❌ ERROR!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except FileNotFoundError:
        print(f"❌ Audio file not found: {audio_file_path}")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - API took too long to respond")
        print(f"   This might mean:")
        print(f"   - Server is starting up (try again in 30 seconds)")
        print(f"   - Audio file is too large")
        print(f"   - Server is overloaded")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - Cannot reach API")
        print(f"   This might mean:")
        print(f"   - API URL is wrong")
        print(f"   - Server is not running")
        print(f"   - Network issues")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None


def test_api_errors(api_url: str = None):
    """Test API error handling"""
    
    if api_url is None:
        api_url = API_URL
    
    print(f"\n{'='*60}")
    print(f"Testing Error Handling")
    print(f"{'='*60}")
    
    # Test 1: Invalid API Key
    print("\n🧪 Test 1: Invalid API Key")
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json", "x-api-key": "invalid_key"},
            json={"language": "English", "audioFormat": "mp3", "audioBase64": "test"},
            timeout=10
        )
        print(f"   Status: {response.status_code} (expected 401)")
        print(f"   Response: {response.json()}")
        if response.status_code == 401:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL - Should return 401")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 2: Missing API Key
    print("\n🧪 Test 2: Missing API Key")
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json={"language": "English", "audioFormat": "mp3", "audioBase64": "test"},
            timeout=10
        )
        print(f"   Status: {response.status_code} (expected 401)")
        print(f"   Response: {response.json()}")
        if response.status_code == 401:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL - Should return 401")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Test 3: Invalid base64
    print("\n🧪 Test 3: Invalid Base64")
    try:
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json", "x-api-key": API_KEY},
            json={"language": "English", "audioFormat": "mp3", "audioBase64": "not_valid_base64!!!"},
            timeout=10
        )
        print(f"   Status: {response.status_code} (expected 400)")
        print(f"   Response: {response.json()}")
        if response.status_code == 400:
            print("   ✅ PASS")
        else:
            print("   ❌ FAIL - Should return 400")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def test_health_check(base_url: str = None):
    """Test health check endpoint"""
    
    if base_url is None:
        base_url = API_URL.replace('/api/voice-detection', '')
    
    health_url = f"{base_url}/health"
    
    print(f"\n{'='*60}")
    print(f"Testing Health Check")
    print(f"URL: {health_url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✅ Health check PASSED")
            return True
        else:
            print("❌ Health check FAILED")
            return False
    except Exception as e:
        print(f"❌ Cannot reach health endpoint: {str(e)}")
        return False


def print_usage():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("AI VOICE DETECTION API - TEST SCRIPT")
    print("="*60)
    print("\nUsage:")
    print("  python test_api.py <audio_file> <language> [api_url]")
    print("\nExamples:")
    print("  # Test locally")
    print("  python test_api.py sample_voice_1.mp3 English")
    print("\n  # Test on Railway")
    print("  python test_api.py sample_voice_1.mp3 Tamil https://your-app.up.railway.app/api/voice-detection")
    print("\n  # Test English audio")
    print("  python test_api.py sample.mp3 English https://your-app.up.railway.app/api/voice-detection")
    print("\nSupported Languages:")
    print("  - Tamil")
    print("  - English")
    print("  - Hindi")
    print("  - Malayalam")
    print("  - Telugu")
    print("\n" + "="*60)


if __name__ == "__main__":
    print("\n🚀 Starting API Tests\n")
    
    # Parse arguments
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)
    
    audio_file = sys.argv[1]
    language = sys.argv[2]
    
    # Get API URL from command line or use default
    if len(sys.argv) > 3:
        api_url = sys.argv[3]
        base_url = api_url.replace('/api/voice-detection', '')
    else:
        api_url = API_URL
        base_url = API_URL.replace('/api/voice-detection', '')
    
    # Check if it's a Railway URL
    is_railway = 'railway.app' in api_url or 'up.railway.app' in api_url
    is_render = 'onrender.com' in api_url
    is_local = 'localhost' in api_url or '127.0.0.1' in api_url
    
    if is_railway:
        print("🚂 Testing on RAILWAY deployment")
    elif is_render:
        print("🎨 Testing on RENDER deployment")
    elif is_local:
        print("💻 Testing on LOCAL deployment")
    else:
        print("🌐 Testing on REMOTE deployment")
    
    # Run health check first
    health_ok = test_health_check(base_url)
    
    if not health_ok and not is_local:
        print("\n⚠️  WARNING: Health check failed!")
        print("   The API might not be ready yet.")
        print("   For Railway/Render deployments, wait 30-60 seconds after deployment.")
        response = input("\n   Continue with tests anyway? (y/n): ")
        if response.lower() != 'y':
            print("\n   Exiting...")
            sys.exit(1)
    
    # Test with sample audio
    print("\n" + "="*60)
    print("MAIN TEST - Real Audio Classification")
    print("="*60)
    result = test_api_with_sample(audio_file, language, api_url)
    
    # Test error handling
    if result:
        test_api_errors(api_url)
    
    # Final summary
    print(f"\n{'='*60}")
    if result:
        print("✅ All tests completed successfully!")
        print(f"\n📋 SUBMISSION INFO:")
        print(f"   Endpoint: {api_url}")
        print(f"   API Key: {API_KEY}")
    else:
        print("❌ Some tests failed!")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if API is running")
        print("   2. Verify the API URL is correct")
        print("   3. Check Railway/Render logs for errors")
        print("   4. Make sure audio file exists and is valid MP3")
    print(f"{'='*60}\n")
