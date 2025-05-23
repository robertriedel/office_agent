"""
Manages email drafting functionalities for the Personal AI Agent.

This module provides functions to save email drafts to the filesystem.
Drafts are stored as text files in a predefined directory, containing
recipient, subject, and body information.
"""
import os
from datetime import datetime

# Directory where email drafts are stored. This is relative to the agent's execution path.
DRAFTS_DIR = "drafts"

def draft_email(recipient: str, subject: str, body: str) -> bool:
    """
    Saves a draft of an email to a new file in the 'drafts' directory.

    The filename includes a sanitized version of the recipient's email and a
    timestamp to ensure uniqueness (e.g., "draft_to_recipient_YYYYMMDD_HHMMSS.txt").
    The 'drafts' directory is created automatically if it doesn't already exist.
    The email content is formatted with "To:", "Subject:", and "Body:" headers.

    Args:
        recipient: The email address of the recipient.
        subject: The subject line of the email.
        body: The main content (body) of the email.
              If recipient, subject, or body is empty, the function will print
              an error and return False.

    Returns:
        True if the email draft was saved successfully, False otherwise (e.g.,
        due to file I/O errors or empty required fields).
    """
    # Validate that all required fields are provided.
    if not all([recipient, subject, body]):
        print("Error: Recipient, subject, and body cannot be empty for an email draft.")
        return False

    try:
        # Ensure the 'drafts' directory exists, create it if not.
        if not os.path.exists(DRAFTS_DIR):
            os.makedirs(DRAFTS_DIR) # Handles creation of parent dirs if necessary
            print(f"Created drafts directory: {DRAFTS_DIR}")

        # Generate a unique filename using recipient and timestamp.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize the recipient string to create a safe filename.
        # Replace non-alphanumeric characters (excluding '.', '_') with underscores.
        safe_recipient = "".join(c if c.isalnum() or c in ['.', '_'] else '_' for c in recipient)
        
        filename = f"draft_to_{safe_recipient}_{timestamp}.txt"
        filepath = os.path.join(DRAFTS_DIR, filename)

        # Format the email content clearly with headers.
        email_content = f"To: {recipient}\nSubject: {subject}\n\nBody:\n{body}"

        # Write the email content to the file using UTF-8 encoding.
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(email_content)
        
        print(f"Email draft saved successfully to {filepath}")
        return True

    except IOError as e_io:
        # Handle specific file input/output errors.
        print(f"Error saving email draft: File I/O error - {e_io}")
        return False
    except Exception as e_unexpected:
        # Catch any other unexpected errors during the process.
        print(f"An unexpected error occurred while saving the email draft: {e_unexpected}")
        return False
