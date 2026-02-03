"""
Session management for multi-turn conversations.

This module stores and manages conversation sessions in memory.
Each session tracks:
- Conversation history
- Scam detection status
- Extracted intelligence
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionData:
    """Data stored for each conversation session"""
    session_id: str
    created_at: datetime
    message_count: int = 0
    scam_detected: bool = False
    confidence: float = 0.0
    conversation_history: List[Dict] = field(default_factory=list)
    extracted_intelligence: Dict = field(default_factory=lambda: {
        "upiIds": [],
        "bankAccounts": [],
        "phoneNumbers": [],
        "ifscCodes": [],
        "phishingLinks": [],
        "suspiciousKeywords": []
    })
    indicators: List[str] = field(default_factory=list)


# In-memory storage (simple dictionary)
_sessions: Dict[str, SessionData] = {}


def get_session(session_id: str) -> Optional[SessionData]:
    """
    Get session by ID.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        SessionData if found, None otherwise
    """
    return _sessions.get(session_id, None)


def create_session(session_id: str) -> SessionData:
    """
    Create new session with given ID.
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        Newly created SessionData
    """
    session = SessionData(
        session_id=session_id,
        created_at=datetime.now()
    )
    _sessions[session_id] = session
    return session


def update_session(
    session_id: str,
    message_count: int = None,
    scam_detected: bool = None,
    confidence: float = None,
    new_message: Dict = None,
    extracted_intelligence: Dict = None,
    indicators: List[str] = None
) -> Optional[SessionData]:
    """
    Update existing session.
    Only updates fields that are not None.
    
    Args:
        session_id: Session to update
        message_count: New message count
        scam_detected: Whether scam was detected
        confidence: Detection confidence score
        new_message: New message to add to history
        extracted_intelligence: New intelligence to merge
        indicators: New indicators to add
    
    Returns:
        Updated SessionData, or None if session not found
    """
    session = _sessions.get(session_id)
    
    if not session:
        return None
    
    # Update message count
    if message_count is not None:
        session.message_count = message_count
    
    # Update scam detection status
    if scam_detected is not None:
        session.scam_detected = scam_detected
    
    # Update confidence
    if confidence is not None:
        session.confidence = confidence
    
    # Add new message to history
    if new_message is not None:
        session.conversation_history.append(new_message)
    
    # Merge extracted intelligence
    if extracted_intelligence is not None:
        for key, values in extracted_intelligence.items():
            if key in session.extracted_intelligence:
                # Add new values without duplicates
                for value in values:
                    if value not in session.extracted_intelligence[key]:
                        session.extracted_intelligence[key].append(value)
    
    # Add new indicators
    if indicators is not None:
        for indicator in indicators:
            if indicator not in session.indicators:
                session.indicators.append(indicator)
    
    return session


def should_send_callback(session: SessionData) -> bool:
    """
    Check if conversation is complete and callback should be sent.
    
    Returns True if:
        - message_count >= 10, OR
        - total extracted intelligence items >= 2
    
    Args:
        session: Session to check
    
    Returns:
        True if callback should be sent, False otherwise
    """
    # Check message count
    if session.message_count >= 10:
        return True
    
    # Count total extracted items
    intel = session.extracted_intelligence
    total_items = (
        len(intel.get("upiIds", [])) +
        len(intel.get("bankAccounts", [])) +
        len(intel.get("phoneNumbers", [])) +
        len(intel.get("ifscCodes", [])) +
        len(intel.get("phishingLinks", []))
    )
    
    if total_items >= 2:
        return True
    
    return False


def delete_session(session_id: str) -> bool:
    """
    Delete session from storage.
    
    Args:
        session_id: Session to delete
    
    Returns:
        True if deleted, False if not found
    """
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def get_all_sessions() -> Dict[str, SessionData]:
    """
    Get all sessions (for debugging).
    
    Returns:
        Dictionary of all sessions
    """
    return _sessions.copy()


def clear_all_sessions() -> None:
    """
    Clear all sessions (for testing).
    """
    _sessions.clear()