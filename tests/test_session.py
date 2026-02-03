"""
Test session management module
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.session import (
    SessionData,
    get_session,
    create_session,
    update_session,
    should_send_callback,
    delete_session,
    clear_all_sessions
)


def test_session():
    """Test session management functions"""
    
    # Clear any existing sessions
    clear_all_sessions()
    
    # Test 1: Create session
    session = create_session("test-123")
    print(f"✅ Create session: {session.session_id}")
    assert session.session_id == "test-123"
    assert session.message_count == 0
    
    # Test 2: Get session
    retrieved = get_session("test-123")
    print(f"✅ Get session: {retrieved.session_id}")
    assert retrieved is not None
    assert retrieved.session_id == "test-123"
    
    # Test 3: Get non-existent session
    not_found = get_session("does-not-exist")
    print(f"✅ Non-existent session: {not_found}")
    assert not_found is None
    
    # Test 4: Update session
    updated = update_session(
        "test-123",
        message_count=5,
        scam_detected=True,
        confidence=0.85,
        new_message={"sender": "scammer", "text": "Hello"},
        extracted_intelligence={"upiIds": ["test@upi"]},
        indicators=["urgency"]
    )
    print(f"✅ Update session: count={updated.message_count}, scam={updated.scam_detected}")
    assert updated.message_count == 5
    assert updated.scam_detected == True
    assert updated.confidence == 0.85
    assert len(updated.conversation_history) == 1
    assert "test@upi" in updated.extracted_intelligence["upiIds"]
    assert "urgency" in updated.indicators
    
    # Test 5: Should send callback - not yet
    should_send = should_send_callback(updated)
    print(f"✅ Should send callback (count=5, items=1): {should_send}")
    assert should_send == False
    
    # Test 6: Add more intelligence
    update_session(
        "test-123",
        extracted_intelligence={"phoneNumbers": ["+911234567890"]}
    )
    session = get_session("test-123")
    should_send = should_send_callback(session)
    print(f"✅ Should send callback (count=5, items=2): {should_send}")
    assert should_send == True  # Now 2 items
    
    # Test 7: Should send callback - message count
    clear_all_sessions()
    session = create_session("test-456")
    update_session("test-456", message_count=10)
    session = get_session("test-456")
    should_send = should_send_callback(session)
    print(f"✅ Should send callback (count=10): {should_send}")
    assert should_send == True
    
    # Test 8: Delete session
    deleted = delete_session("test-456")
    print(f"✅ Delete session: {deleted}")
    assert deleted == True
    
    # Test 9: Delete non-existent session
    deleted = delete_session("does-not-exist")
    print(f"✅ Delete non-existent: {deleted}")
    assert deleted == False
    
    print("\n🎉 All session tests passed!")


if __name__ == '__main__':
    test_session()