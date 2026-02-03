"""
Test callback module
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.session import SessionData
from src.callback import build_callback_payload, generate_agent_notes


def test_callback():
    """Test callback functions"""
    
    # Create a test session
    session = SessionData(
        session_id="test-callback-123",
        created_at=datetime.now(),
        message_count=8,
        scam_detected=True,
        confidence=0.92,
        conversation_history=[
            {"sender": "scammer", "text": "Your account is blocked!"},
            {"sender": "agent", "text": "Oh no! What should I do?"},
            {"sender": "scammer", "text": "Send money to this UPI: fraud@upi"},
            {"sender": "agent", "text": "How much should I send?"}
        ],
        extracted_intelligence={
            "upiIds": ["fraud@upi"],
            "bankAccounts": [],
            "phoneNumbers": ["+919876543210"],
            "ifscCodes": [],
            "phishingLinks": ["http://fake-bank.com"],
            "suspiciousKeywords": ["blocked", "urgent"]
        },
        indicators=["urgency", "authority"]
    )
    
    # Test 1: Generate agent notes
    notes = generate_agent_notes(session)
    print(f"✅ Agent notes generated:")
    print(f"   {notes}")
    assert "Scam detected" in notes
    assert "92%" in notes
    assert "urgency" in notes or "authority" in notes
    
    # Test 2: Build callback payload
    payload = build_callback_payload(session)
    print(f"\n✅ Callback payload built:")
    print(f"   Session ID: {payload['sessionId']}")
    print(f"   Scam Detected: {payload['scamDetected']}")
    print(f"   Messages: {payload['totalMessagesExchanged']}")
    print(f"   UPI IDs: {payload['extractedIntelligence']['upiIds']}")
    print(f"   Phone Numbers: {payload['extractedIntelligence']['phoneNumbers']}")
    
    assert payload["sessionId"] == "test-callback-123"
    assert payload["scamDetected"] == True
    assert payload["totalMessagesExchanged"] == 8
    assert "fraud@upi" in payload["extractedIntelligence"]["upiIds"]
    assert "+919876543210" in payload["extractedIntelligence"]["phoneNumbers"]
    assert "agentNotes" in payload
    
    # Test 3: Payload with custom notes
    custom_notes = "This is a custom note about the scammer."
    payload_custom = build_callback_payload(session, custom_notes)
    print(f"\n✅ Custom notes payload:")
    print(f"   Notes: {payload_custom['agentNotes']}")
    assert payload_custom["agentNotes"] == custom_notes
    
    # Test 4: Empty session
    empty_session = SessionData(
        session_id="empty-session",
        created_at=datetime.now(),
        message_count=2,
        scam_detected=False,
        confidence=0.1
    )
    empty_payload = build_callback_payload(empty_session)
    print(f"\n✅ Empty session payload:")
    print(f"   Scam Detected: {empty_payload['scamDetected']}")
    print(f"   UPI IDs: {empty_payload['extractedIntelligence']['upiIds']}")
    assert empty_payload["scamDetected"] == False
    assert empty_payload["extractedIntelligence"]["upiIds"] == []
    
    print("\n🎉 All callback tests passed!")


if __name__ == '__main__':
    test_callback()