#!/usr/bin/env python3
"""
Generate base64 encoded audio for testing the API
"""

import base64
import sys


def encode_audio_file(file_path: str) -> str:
    """Encode an audio file to base64"""
    try:
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            return base64_audio
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def create_curl_command(base64_audio: str, language: str, api_url: str, api_key: str):
    """Generate a curl command for testing"""
    
    # Truncate base64 for display
    display_audio = base64_audio[:50] + "..." if len(base64_audio) > 50 else base64_audio
    
    curl_command = f"""
curl -X POST {api_url} \\
  -H "Content-Type: application/json" \\
  -H "x-api-key: {api_key}" \\
  -d '{{
    "language": "{language}",
    "audioFormat": "mp3",
    "audioBase64": "{base64_audio}"
  }}'
"""
    
    print("\n" + "="*60)
    print("CURL COMMAND (use this to test your API)")
    print("="*60)
    print(curl_command)
    
    # Also create a JSON file
    json_payload = f"""{{
  "language": "{language}",
  "audioFormat": "mp3",
  "audioBase64": "{base64_audio}"
}}"""
    
    with open("test_payload.json", "w") as f:
        f.write(json_payload)
    
    print("\n✓ Test payload saved to: test_payload.json")
    print("\nYou can also use:")
    print(f"  curl -X POST {api_url} \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(f"    -H 'x-api-key: {api_key}' \\")
    print(f"    -d @test_payload.json")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python encode_audio.py <audio_file.mp3> [language] [api_url]")
        print("\nExample:")
        print("  python encode_audio.py sample.mp3 English http://localhost:8000/api/voice-detection")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "English"
    api_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000/api/voice-detection"
    api_key = "sk_test_123456789"
    
    print(f"\nEncoding audio file: {audio_file}")
    base64_audio = encode_audio_file(audio_file)
    
    if base64_audio:
        print(f"✓ Successfully encoded {len(base64_audio)} characters")
        print(f"✓ Language: {language}")
        print(f"✓ API URL: {api_url}")
        
        create_curl_command(base64_audio, language, api_url, api_key)
        
        print("\n" + "="*60)
        print("READY TO TEST!")
        print("="*60)
        print("\n1. Make sure your API is running")
        print("2. Use the curl command above to test")
        print("3. Or use: curl -X POST ... -d @test_payload.json")
    else:
        sys.exit(1)
