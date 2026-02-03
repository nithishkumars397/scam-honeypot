"""
GUVI Callback module.

This module sends the final extracted intelligence
to GUVI's API when a conversation is complete.
"""

import os
import requests
from typing import Dict
from src.session import SessionData


def build_callback_payload(session: SessionData, agent_notes: str = "") -> Dict:
    """
    Builds the payload for GUVI callback.
    
    Args:
        session: Completed session data
        agent_notes: Summary of scammer behavior
    
    Returns:
        Dictionary formatted for GUVI API
    """
    
    # Generate agent notes if not provided
    if not agent_notes:
        agent_notes = generate_agent_notes(session)
    
    payload = {
        "sessionId": session.session_id,
        "scamDetected": session.scam_detected,
        "totalMessagesExchanged": session.message_count,
        "extractedIntelligence": {
            "upiIds": session.extracted_intelligence.get("upiIds", []),
            "bankAccounts": session.extracted_intelligence.get("bankAccounts", []),
            "phoneNumbers": session.extracted_intelligence.get("phoneNumbers", []),
            "ifscCodes": session.extracted_intelligence.get("ifscCodes", []),
            "phishingLinks": session.extracted_intelligence.get("phishingLinks", []),
            "suspiciousKeywords": session.extracted_intelligence.get("suspiciousKeywords", [])
        },
        "agentNotes": agent_notes
    }
    
    return payload


def generate_agent_notes(session: SessionData) -> str:
    """
    Generate summary notes about the scammer's behavior.
    
    Args:
        session: Session data with conversation history
    
    Returns:
        String summary of scammer tactics
    """
    notes_parts = []
    
    # Add scam detection status
    if session.scam_detected:
        notes_parts.append(f"Scam detected with {session.confidence:.0%} confidence.")
    else:
        notes_parts.append("No scam detected.")
    
    # Add indicators found
    if session.indicators:
        tactics = ", ".join(session.indicators)
        notes_parts.append(f"Tactics used: {tactics}.")
    
    # Add intelligence summary
    intel = session.extracted_intelligence
    intel_found = []
    
    if intel.get("upiIds"):
        intel_found.append(f"{len(intel['upiIds'])} UPI ID(s)")
    if intel.get("bankAccounts"):
        intel_found.append(f"{len(intel['bankAccounts'])} bank account(s)")
    if intel.get("phoneNumbers"):
        intel_found.append(f"{len(intel['phoneNumbers'])} phone number(s)")
    if intel.get("phishingLinks"):
        intel_found.append(f"{len(intel['phishingLinks'])} phishing link(s)")
    
    if intel_found:
        notes_parts.append(f"Extracted: {', '.join(intel_found)}.")
    
    # Add conversation length
    notes_parts.append(f"Conversation lasted {session.message_count} messages.")
    
    return " ".join(notes_parts)


def send_final_callback(session: SessionData, agent_notes: str = "") -> bool:
    """
    Sends final intelligence to GUVI.
    
    Args:
        session: Completed session data
        agent_notes: Summary of scammer behavior
    
    Returns:
        True if successful, False otherwise
    
    Endpoint:
        POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
    """
    
    # Get callback URL from environment
    callback_url = os.getenv(
        'GUVI_CALLBACK_URL',
        'https://hackathon.guvi.in/api/updateHoneyPotFinalResult'
    )
    
    # Build payload
    payload = build_callback_payload(session, agent_notes)
    
    try:
        # Send POST request
        response = requests.post(
            callback_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Check if successful
        if response.status_code == 200:
            print(f"✅ Callback sent successfully for session: {session.session_id}")
            return True
        else:
            print(f"❌ Callback failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Callback timeout for session: {session.session_id}")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Callback error: {str(e)}")
        return False