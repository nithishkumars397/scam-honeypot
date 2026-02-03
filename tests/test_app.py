"""
Test Flask application
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables before importing app
os.environ['API_SECRET_KEY'] = 'test_secret_123'

import json
from src.app import app
from src.session import clear_all_sessions


def test_app():
    """Test Flask application endpoints"""
    
    # Create test client
    client = app.test_client()
    
    # Clear sessions before testing
    clear_all_sessions()
    
    # ========================================
    # Test 1: Health Check
    # ========================================
    print("Testing health endpoint...")
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    print("✅ Health check passed")
    
    # ========================================
    # Test 2: Honeypot without API key
    # ========================================
    print("\nTesting honeypot without API key...")
    response = client.post('/honeypot', json={
        "sessionId": "test-1",
        "message": {"sender": "scammer", "text": "Hello"}
    })
    assert response.status_code == 401
    print("✅ Unauthorized test passed")
    
    # ========================================
    # Test 3: Honeypot with valid API key
    # ========================================
    print("\nTesting honeypot with valid request...")
    response = client.post(
        '/honeypot',
        json={
            "sessionId": "test-session-123",
            "message": {
                "sender": "scammer",
                "text": "Your bank account is blocked! Verify immediately.",
                "timestamp": 1234567890
            },
            "conversationHistory": [],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        },
        headers={'x-api-key': 'test_secret_123'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'reply' in data
    print(f"✅ Honeypot response: {data['reply'][:50]}...")
    
    # ========================================
    # Test 4: Check session was created
    # ========================================
    print("\nTesting session endpoint...")
    response = client.get(
        '/session/test-session-123',
        headers={'x-api-key': 'test_secret_123'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['session']['messageCount'] == 2  # scammer + agent
    assert data['session']['scamDetected'] == True
    print(f"✅ Session info: messages={data['session']['messageCount']}, scam={data['session']['scamDetected']}")
    
    # ========================================
    # Test 5: Multiple messages in session
    # ========================================
    print("\nTesting multiple messages...")
    response = client.post(
        '/honeypot',
        json={
            "sessionId": "test-session-123",
            "message": {
                "sender": "scammer",
                "text": "Send money to this UPI: fraud@paytm",
                "timestamp": 1234567891
            },
            "conversationHistory": []
        },
        headers={'x-api-key': 'test_secret_123'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    print(f"✅ Second message reply: {data['reply'][:50]}...")
    
    # Check session updated
    response = client.get(
        '/session/test-session-123',
        headers={'x-api-key': 'test_secret_123'}
    )
    data = json.loads(response.data)
    assert data['session']['messageCount'] == 4
    assert 'fraud@paytm' in data['session']['extractedIntelligence']['upiIds']
    print(f"✅ UPI extracted: {data['session']['extractedIntelligence']['upiIds']}")
    
    # ========================================
    # Test 6: Missing required fields
    # ========================================
    print("\nTesting missing fields...")
    response = client.post(
        '/honeypot',
        json={"message": {"text": "test"}},  # Missing sessionId
        headers={'x-api-key': 'test_secret_123'}
    )
    assert response.status_code == 400
    print("✅ Missing field validation passed")
    
    # ========================================
    # Test 7: 404 endpoint
    # ========================================
    print("\nTesting 404...")
    response = client.get('/nonexistent')
    assert response.status_code == 404
    print("✅ 404 handling passed")
    
    # Clean up
    clear_all_sessions()
    
    print("\n🎉 All app tests passed!")


if __name__ == '__main__':
    test_app()