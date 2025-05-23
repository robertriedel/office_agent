"""
Manages note-taking functionalities for the Personal AI Agent.

This module provides functions to save new notes to the filesystem
and list existing notes. Notes are stored as text files in a predefined
directory.
"""
import os
from datetime import datetime

# Directory where notes are stored. This is relative to the agent's execution path.
NOTES_DIR = "notes"

def save_note(note_content: str) -> bool:
    """
    Saves the given note content to a new file in the 'notes' directory.

    The filename is generated using a timestamp to ensure uniqueness
    (e.g., "note_YYYYMMDD_HHMMSS.txt").
    The 'notes' directory is created automatically if it doesn't already exist.

    Args:
        note_content: The string content of the note to be saved.
                      If empty, the function will print an error and return False.

    Returns:
        True if the note was saved successfully, False otherwise (e.g., due to
        file I/O errors or empty content).
    """
    if not note_content:
        print("Error: Note content cannot be empty.")
        return False

    try:
        # Ensure the 'notes' directory exists, create it if not.
        # The os.makedirs function also creates parent directories if needed,
        # and doesn't raise an error if the directory already exists (with exist_ok=True).
        if not os.path.exists(NOTES_DIR):
            os.makedirs(NOTES_DIR) # exist_ok=True is default for later Python versions
            print(f"Created notes directory: {NOTES_DIR}")

        # Generate a unique filename using the current date and time.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"note_{timestamp}.txt"
        filepath = os.path.join(NOTES_DIR, filename)

        # Write the note content to the file.
        # Using 'w' mode will overwrite the file if it somehow already exists,
        # though timestamping should make this extremely rare.
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(note_content)
        
        print(f"Note saved successfully to {filepath}")
        return True

    except IOError as e_io:
        # Handle specific file input/output errors.
        print(f"Error saving note: File I/O error - {e_io}")
        return False
    except Exception as e_unexpected:
        # Catch any other unexpected errors during the process.
        print(f"An unexpected error occurred while saving the note: {e_unexpected}")
        return False

def list_notes() -> list[str] | None:
    """
    Lists all valid note files found in the 'notes' directory.

    A valid note file is expected to start with "note_" and end with ".txt".

    Returns:
        A list of note filenames (e.g., ["note_YYYYMMDD_HHMMSS.txt", ...])
        if the directory exists and notes are found.
        Returns an empty list if no valid notes are found in the directory.
        Returns None if the notes directory itself does not exist or if an
        OS-level error occurs while accessing the directory.
    """
    # Check if the notes directory exists first.
    if not os.path.exists(NOTES_DIR):
        print(f"Error: Notes directory '{NOTES_DIR}' does not exist.")
        return None  # Indicate that the source of notes is missing.
    
    try:
        # Get all entries in the notes directory.
        all_entries = os.listdir(NOTES_DIR)
        
        # Filter for files that match the expected note naming convention.
        # This helps avoid listing temporary files or subdirectories if any were present.
        note_files = [
            entry for entry in all_entries 
            if entry.startswith("note_") and entry.endswith(".txt") and \
               os.path.isfile(os.path.join(NOTES_DIR, entry)) # Ensure it's a file
        ]
        
        if not note_files:
            print(f"No notes found in the directory: {NOTES_DIR}")
            return []  # Return an empty list, which is distinct from None (directory error).
        
        print(f"Found notes: {note_files}")
        return note_files
        
    except OSError as e_os:
        # Handle errors related to accessing the directory (e.g., permission issues).
        print(f"Error accessing the notes directory: {e_os}")
        return None # Indicate an issue with accessing the directory.
    except Exception as e_unexpected:
        # Catch any other unexpected errors.
        print(f"An unexpected error occurred while listing notes: {e_unexpected}")
        return None
