"""
Test authentication module
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from src.auth import validate_api_key


def test_auth():
    """Test API key validation"""
    
    # Create test Flask app
    app = Flask(__name__)
    
    # Set test secret key
    os.environ['API_SECRET_KEY'] = 'test_secret_123'
    
    with app.test_request_context(headers={'x-api-key': 'test_secret_123'}):
        from flask import request
        result = validate_api_key(request)
        print(f"✅ Valid key test: {result}")  # Should be True
        assert result == True
    
    with app.test_request_context(headers={'x-api-key': 'wrong_key'}):
        from flask import request
        result = validate_api_key(request)
        print(f"✅ Invalid key test: {result}")  # Should be False
        assert result == False
    
    with app.test_request_context(headers={}):
        from flask import request
        result = validate_api_key(request)
        print(f"✅ Missing key test: {result}")  # Should be False
        assert result == False
    
    print("\n🎉 All auth tests passed!")


if __name__ == '__main__':
    test_auth()