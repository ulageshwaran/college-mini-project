"""
Test script to see actual Gemini API response structure
Run: python test_gemini_response.py
"""
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Test API call
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Write a simple recipe for pasta."
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 500,
    }
}

headers = {
    "Content-Type": "application/json"
}

print("\n🔄 Making API request...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📋 Full Response Structure:")
        print(json.dumps(data, indent=2))
        
        print("\n" + "="*50)
        print("🔍 Extracting Recipe:")
        print("="*50)
        
        try:
            # Try to extract the text
            if 'candidates' in data:
                candidate = data['candidates'][0]
                print(f"✅ Found candidates: {len(data['candidates'])}")
                
                if 'content' in candidate:
                    content = candidate['content']
                    print(f"✅ Found content")
                    
                    if 'parts' in content:
                        parts = content['parts']
                        print(f"✅ Found parts: {len(parts)}")
                        
                        if len(parts) > 0 and 'text' in parts[0]:
                            recipe = parts[0]['text']
                            print("\n📝 Recipe Text:")
                            print(recipe)
                        else:
                            print("❌ No text in parts")
                    else:
                        print("❌ No 'parts' in content")
                        print(f"Content keys: {content.keys()}")
                else:
                    print("❌ No 'content' in candidate")
                    print(f"Candidate keys: {candidate.keys()}")
            else:
                print("❌ No 'candidates' in response")
                print(f"Response keys: {data.keys()}")
                
        except Exception as e:
            print(f"\n❌ Error extracting text: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n❌ API Error:")
        print(json.dumps(response.json(), indent=2))
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")
    import traceback
    traceback.print_exc()