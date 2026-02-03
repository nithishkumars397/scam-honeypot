"""
Flask Application - Main API Endpoint

This is the main honeypot API that:
1. Receives scammer messages
2. Detects if it's a scam
3. Extracts intelligence
4. Generates agent replies
5. Sends callback when complete
"""

import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from src.auth import validate_api_key
from src.session import (
    get_session,
    create_session,
    update_session,
    should_send_callback,
    delete_session
)
from src.callback import send_final_callback

# Import Member A's modules (will be added later)
# from src.detector import detect_scam
# from src.extractor import extract_intelligence
# from src.agent import generate_agent_reply

# Create Flask app
app = Flask(__name__)


# ============================================
# TEMPORARY PLACEHOLDER FUNCTIONS
# These will be replaced by Member A's code
# ============================================

def detect_scam(message: str, conversation_history: list = None):
    """
    PLACEHOLDER - Will be replaced by Member A's detector.py
    
    Returns: (is_scam, confidence, indicators)
    """
    # Simple keyword-based detection for now
    scam_keywords = [
        'blocked', 'suspended', 'verify', 'urgent', 'immediately',
        'account', 'bank', 'otp', 'pin', 'password', 'lottery',
        'winner', 'prize', 'claim', 'expire', 'limited time',
        'act now', 'transfer', 'pay', 'upi', 'kyc'
    ]
    
    message_lower = message.lower()
    found_keywords = [kw for kw in scam_keywords if kw in message_lower]
    
    if len(found_keywords) >= 2:
        confidence = min(0.5 + (len(found_keywords) * 0.1), 0.99)
        return True, confidence, found_keywords
    elif len(found_keywords) == 1:
        return True, 0.4, found_keywords
    else:
        return False, 0.1, []


def extract_intelligence(message: str):
    """
    PLACEHOLDER - Will be replaced by Member A's extractor.py
    
    Returns: dict with extracted data
    """
    import re
    
    result = {
        "upiIds": [],
        "bankAccounts": [],
        "phoneNumbers": [],
        "ifscCodes": [],
        "phishingLinks": [],
        "suspiciousKeywords": []
    }
    
    # UPI ID pattern
    upi_pattern = r'[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}'
    result["upiIds"] = re.findall(upi_pattern, message)
    
    # Phone number pattern (Indian)
    phone_pattern = r'(?:\+91[\-\s]?)?[6-9]\d{9}'
    result["phoneNumbers"] = re.findall(phone_pattern, message)
    
    # Bank account pattern (10-18 digits)
    bank_pattern = r'\b\d{10,18}\b'
    result["bankAccounts"] = re.findall(bank_pattern, message)
    
    # IFSC pattern
    ifsc_pattern = r'[A-Z]{4}0[A-Z0-9]{6}'
    result["ifscCodes"] = re.findall(ifsc_pattern, message.upper())
    
    # URL pattern
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    result["phishingLinks"] = re.findall(url_pattern, message)
    
    # Suspicious keywords
    keywords = ['urgent', 'blocked', 'verify', 'otp', 'pin', 'expire']
    message_lower = message.lower()
    result["suspiciousKeywords"] = [kw for kw in keywords if kw in message_lower]
    
    return result


def generate_agent_reply(current_message: str, conversation_history: list, scam_indicators: list = None):
    """
    PLACEHOLDER - Will be replaced by Member A's agent.py
    
    Returns: Agent reply string
    """
    # Simple responses based on message count
    msg_count = len(conversation_history) if conversation_history else 0
    
    responses = [
        "Oh dear, this is very worrying! What happened to my account?",
        "I don't understand these technical things. Can you explain more simply?",
        "My grandson usually helps me with this. What should I do?",
        "This sounds urgent! How can I fix this problem?",
        "I'm confused. Where should I send the money?",
        "Let me write this down. What was that number again?",
        "Oh my! I hope I don't lose my savings. Tell me what to do.",
        "Should I go to the bank? Or can I do it on my phone?",
        "I'm not good with computers. Can you guide me step by step?",
        "Thank you for helping me. What information do you need?"
    ]
    
    # Select response based on message count
    index = msg_count % len(responses)
    return responses[index]


# ============================================
# API ROUTES
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Render.
    
    Returns:
        {"status": "healthy"}
    """
    return jsonify({"status": "healthy"}), 200


@app.route('/honeypot', methods=['POST'])
def honeypot_endpoint():
    """
    Main honeypot API endpoint.
    
    Receives scammer messages and returns agent replies.
    
    Request format:
    {
        "sessionId": "unique-session-id",
        "message": {
            "sender": "scammer",
            "text": "Your account is blocked!",
            "timestamp": 1234567890
        },
        "conversationHistory": [...],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    Response format:
    {
        "status": "success",
        "reply": "Oh no! What should I do?"
    }
    """
    
    # ========================================
    # Step 1: Validate API Key
    # ========================================
    if not validate_api_key(request):
        return jsonify({
            "status": "error",
            "message": "Unauthorized - Invalid API key"
        }), 401
    
    # ========================================
    # Step 2: Parse Request Body
    # ========================================
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Missing request body"
            }), 400
        
        # Extract required fields
        session_id = data.get('sessionId')
        message_data = data.get('message', {})
        conversation_history = data.get('conversationHistory', [])
        metadata = data.get('metadata', {})
        
        # Validate required fields
        if not session_id:
            return jsonify({
                "status": "error",
                "message": "Missing sessionId"
            }), 400
        
        if not message_data or not message_data.get('text'):
            return jsonify({
                "status": "error",
                "message": "Missing message text"
            }), 400
        
        message_text = message_data.get('text', '')
        message_sender = message_data.get('sender', 'scammer')
        message_timestamp = message_data.get('timestamp', 0)
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Invalid request format: {str(e)}"
        }), 400
    
    # ========================================
    # Step 3: Get or Create Session
    # ========================================
    session = get_session(session_id)
    
    if not session:
        session = create_session(session_id)
        print(f"📝 New session created: {session_id}")
    else:
        print(f"📂 Existing session: {session_id} (messages: {session.message_count})")
    
    # ========================================
    # Step 4: Detect Scam
    # ========================================
    is_scam, confidence, indicators = detect_scam(
        message_text,
        session.conversation_history
    )
    
    print(f"🔍 Scam detection: {is_scam} (confidence: {confidence:.2f})")
    
    # ========================================
    # Step 5: Extract Intelligence
    # ========================================
    extracted = extract_intelligence(message_text)
    
    # Log what was extracted
    for key, values in extracted.items():
        if values:
            print(f"🎯 Extracted {key}: {values}")
    
    # ========================================
    # Step 6: Generate Agent Reply
    # ========================================
    agent_reply = generate_agent_reply(
        message_text,
        session.conversation_history,
        indicators
    )
    
    print(f"🤖 Agent reply: {agent_reply[:50]}...")
    
    # ========================================
    # Step 7: Update Session
    # ========================================
    
    # Add scammer message to history
    update_session(
        session_id,
        new_message={
            "sender": message_sender,
            "text": message_text,
            "timestamp": message_timestamp
        }
    )
    
    # Add agent reply to history
    import time
    update_session(
        session_id,
        new_message={
            "sender": "agent",
            "text": agent_reply,
            "timestamp": int(time.time() * 1000)
        }
    )
    
    # Update session with new data
    session = update_session(
        session_id,
        message_count=session.message_count + 2,  # scammer + agent
        scam_detected=is_scam or session.scam_detected,
        confidence=max(confidence, session.confidence),
        extracted_intelligence=extracted,
        indicators=indicators
    )
    
    # ========================================
    # Step 8: Check if Callback Needed
    # ========================================
    if should_send_callback(session):
        print(f"📤 Sending callback for session: {session_id}")
        
        # Send callback to GUVI
        callback_success = send_final_callback(session)
        
        if callback_success:
            print(f"✅ Callback sent successfully")
            # Delete session after successful callback
            delete_session(session_id)
        else:
            print(f"⚠️ Callback failed, keeping session")
    
    # ========================================
    # Step 9: Return Response
    # ========================================
    return jsonify({
        "status": "success",
        "reply": agent_reply
    }), 200


@app.route('/session/<session_id>', methods=['GET'])
def get_session_info(session_id):
    """
    Debug endpoint to check session status.
    
    Returns session information if found.
    """
    if not validate_api_key(request):
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401
    
    session = get_session(session_id)
    
    if not session:
        return jsonify({
            "status": "error",
            "message": "Session not found"
        }), 404
    
    return jsonify({
        "status": "success",
        "session": {
            "sessionId": session.session_id,
            "messageCount": session.message_count,
            "scamDetected": session.scam_detected,
            "confidence": session.confidence,
            "indicators": session.indicators,
            "extractedIntelligence": session.extracted_intelligence,
            "conversationLength": len(session.conversation_history)
        }
    }), 200


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Scam Honeypot API on port {port}")
    print(f"📍 Health check: http://localhost:{port}/health")
    print(f"📍 Honeypot endpoint: http://localhost:{port}/honeypot")
    
    app.run(host='0.0.0.0', port=port, debug=debug)