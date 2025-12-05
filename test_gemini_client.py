#!/usr/bin/env python3
"""
Simple Gemini client test file to verify API connection and functionality
"""
import os
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test different import methods for Gemini
def test_imports():
    """Test different ways to import Gemini"""
    print("🧪 Testing Gemini imports...")
    
    # try:
    #     import google.generativeai as genai
    #     print("✅ google.generativeai import successful")
    #     return genai, "google.generativeai"
    # except ImportError as e:
    #     print(f"❌ google.generativeai failed: {e}")
    
    try:
        from google import genai
        print("✅ google.genai import successful")
        return genai, "google.genai"
    except ImportError as e:
        print(f"❌ google.genai failed: {e}")
    
    try:
        import genai
        print("✅ genai import successful")
        return genai, "genai"
    except ImportError as e:
        print(f"❌ genai failed: {e}")
    
    print("❌ No working Gemini import found!")
    return None, None

def test_api_key():
    """Test API key configuration"""
    print("\n🔑 Testing API key...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return None
    
    if api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY is still placeholder value")
        return None
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    return api_key

async def test_gemini_connection():
    """Test basic Gemini API connection"""
    print("\n🤖 Testing Gemini API connection...")
    
    # Test imports
    genai, import_method = test_imports()
    if not genai:
        return False
    
    # Test API key
    api_key = test_api_key()
    if not api_key:
        return False
    
    try:
        # Configure based on import method
        if import_method == "google.generativeai":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Test simple generation
            print("🔄 Testing content generation...")
            response = await asyncio.to_thread(
                model.generate_content,
                "Hello! Please respond with just 'API connection successful' and nothing else."
            )
            
            print(f"✅ Response: {response.text.strip()}")
            return True
            
        elif import_method == "google.genai":
            client = genai.Client(api_key=api_key)
            
            print("🔄 Testing content generation...")
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents="Hello! Please respond with just 'API connection successful' and nothing else."
            )
            
            print(f"✅ Response: {response.text.strip()}")
            return True
            
        else:
            print(f"❌ Unknown import method: {import_method}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {str(e)}")
        return False

async def test_json_parsing():
    """Test JSON parsing capability"""
    print("\n📋 Testing JSON parsing...")
    
    genai, import_method = test_imports()
    if not genai:
        return False
    
    api_key = test_api_key()
    if not api_key:
        return False
    
    try:
        # Configure based on import method
        if import_method == "google.generativeai":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = """
Extract information from this text and return ONLY valid JSON:

"John Doe is a software engineer at Tech Corp in San Francisco. He has a Twitter @johndoe and LinkedIn profile. He studied at MIT and specializes in AI."

Return JSON with: name, company, location, twitter, education, expertise.
"""
            
            response = await asyncio.to_thread(model.generate_content, prompt)
            
        elif import_method == "google.genai":
            client = genai.Client(api_key=api_key)
            
            prompt = """
Extract information from this text and return ONLY valid JSON:

"John Doe is a software engineer at Tech Corp in San Francisco. He has a Twitter @johndoe and LinkedIn profile. He studied at MIT and specializes in AI."

Return JSON with: name, company, location, twitter, education, expertise.
"""
            
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt
            )
        
        # Try to parse response as JSON
        response_text = response.text.strip()
        print(f"Raw response: {response_text}")
        
        # Clean JSON markers
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        parsed_json = json.loads(response_text)
        print(f"✅ JSON parsing successful: {json.dumps(parsed_json, indent=2)}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Raw response was: {response_text}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Gemini Client Test Suite")
    print("=" * 50)
    
    # Test basic connection
    connection_ok = await test_gemini_connection()
    
    if connection_ok:
        # Test JSON parsing
        await test_json_parsing()
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Connection failed - fix API setup first")
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Install correct package: pip install google-generativeai")
        print("2. Get API key from: https://makersuite.google.com/app/apikey")
        print("3. Add to .env: GEMINI_API_KEY=your_actual_key")
        print("4. Make sure key has proper permissions")

if __name__ == "__main__":
    asyncio.run(main())