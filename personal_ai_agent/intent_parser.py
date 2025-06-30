"""
Handles parsing of transcribed text to determine user intent.

This module provides functions to analyze text input and identify
predefined intents such as taking a note, sending an email, or listing notes.
"""

def parse_intent(text: str) -> str | None:
    """
    Parses the intent from the transcribed speech based on keywords.

    Args:
        text: The transcribed speech (string) from the user.
              Expected to be in lowercase for reliable matching, though this
              function converts it to lowercase internally.

    Returns:
        A string representing the recognized intent:
        - "take_note": If keywords related to creating a note are found.
        - "list_notes": If keywords related to listing/showing notes are found.
        - "send_email": If keywords related to sending an email are found.
        Returns None if no specific intent is recognized or if the input text is empty.
    """
    if not text:
        return None

    text_lower = text.lower() # Convert to lowercase for case-insensitive matching

    # --- Help intent ---
    if "help" in text_lower or "what can you do" in text_lower:
        return "help"

    # --- Note-related intents ---
    # Check for general "note" or "notes" keywords first.
    if "note" in text_lower or "notes" in text_lower:
        if "search" in text_lower or "find" in text_lower:
            return "search_notes"
        # Keywords for listing notes. Order matters: more specific ("list notes") before general ("note").
        if "list" in text_lower or \
           "show" in text_lower or \
           "read" in text_lower or \
           "what are my" in text_lower or \
           "tell me my" in text_lower:
            return "list_notes"
        # Default to "take_note" if note-related but not list-related.
        else:
            return "take_note"
            
    # --- Email-related intents ---
    elif "email" in text_lower or "mail" in text_lower:
        # Keywords for sending an email.
        return "send_email"

    # --- Meeting Transcription Intents ---
    elif "meeting" in text_lower or "recording" in text_lower or "transcription" in text_lower or "transcribe" in text_lower:
        if "start" in text_lower or "begin" in text_lower:
            return "start_meeting"
        elif "stop" in text_lower or "end" in text_lower:
            return "stop_meeting"
        
    # --- No specific intent recognized ---
    else:
        return None
