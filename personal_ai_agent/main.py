"""
Main application for the Personal AI Agent.

This module sets up and runs the Tkinter-based GUI, handles user interactions
(voice input via a button), and dispatches recognized intents to appropriate
handler functions defined in other modules.
"""
import tkinter as tk
# from tkinter import simpledialog # Potentially useful for future text input dialogs
import os # Added for file operations
from datetime import datetime # Added for timestamping meeting transcripts
from audio_handler import speak, listen_and_transcribe
from intent_parser import parse_intent
from notes_module import save_note, list_notes, NOTES_DIR # Import NOTES_DIR
from email_module import draft_email

# --- Global Variables ---
# status_label: A Tkinter Label widget used to display feedback and status messages to the user in the GUI.
# It's global to allow different functions (intent handlers, button callback) to update it.
status_label = None

# --- Meeting Transcription State ---
is_meeting_recording_active = False
current_meeting_transcript_parts = []
MEETING_TEMP_FILE = "temp_meeting_transcript.txt"

# --- Global Tkinter Root (for root.update()) ---
root: tk.Tk | None = None # Type hint for root

# --- Intent Handler Functions ---

def handle_take_note_intent(command_text: str):
    """
    Handles the 'take_note' intent.

    Prompts the user for the content of the note, transcribes their response,
    and saves the note using `notes_module.save_note`. Updates the GUI
    status label with the outcome.

    Args:
        command_text: The original transcribed text that triggered this intent.
                      Currently unused but passed for consistency.
    """
    global status_label
    if status_label:
        status_label.config(text="Intent: Take Note. What should the note say?")
    
    speak("What would you like the note to say?")
    print("Please say the content of your note:") # Console prompt
    
    note_content = listen_and_transcribe() # Get note content via voice

    if note_content:
        if save_note(note_content):
            feedback = "Note saved successfully."
        else:
            feedback = "Sorry, I couldn't save the note."
    else:
        # This occurs if listen_and_transcribe returned None or an error string
        feedback = "I didn't catch that. Note not saved."
        if isinstance(note_content, str) and note_content.startswith("Google STT error:"):
            feedback = note_content # Show specific STT error

    print(feedback)
    speak(feedback)
    if status_label:
        status_label.config(text=feedback)

def handle_list_notes_intent():
    """
    Handles the 'list_notes' intent.

    Retrieves the list of saved notes using `notes_module.list_notes` and
    presents them to the user via spoken feedback and the GUI status label.
    """
    global status_label
    print("DEBUG: 'List Notes' intent recognized. Calling list_notes().") # For console debugging
    
    notes_list = list_notes() # Call the function from notes_module

    if notes_list is None:
        # This means the notes directory itself probably doesn't exist or is inaccessible.
        feedback = "Could not access the notes directory."
    elif not notes_list: # Empty list means directory exists but no notes found.
        feedback = "You have no notes."
    else:
        # Prepare feedback for speech and GUI
        speak(f"You have {len(notes_list)} notes.")
        gui_status_text = f"Found {len(notes_list)} notes:\n"
        
        notes_to_display_in_gui = []
        for i, note_file in enumerate(notes_list):
            # Clean up filename for better readability
            clean_name = note_file.replace('.txt', '').replace('note_', '').replace('_', ' ')
            if i < 3: # Speak the names of the first 3 notes
                speak(f"Note {i+1}: {clean_name}")
            if i < 5: # Add first 5 notes to the list for GUI display
                notes_to_display_in_gui.append(clean_name)
            print(f"  - {note_file} (Cleaned: {clean_name})") # Log all notes to console

        gui_status_text += "\n".join(notes_to_display_in_gui)
        if len(notes_list) > 5:
            gui_status_text += "\n(and more... see console for full list)"
        feedback = gui_status_text # For GUI
            
    print(feedback if isinstance(feedback, str) else "Displaying notes list.") # Console log
    if status_label:
        status_label.config(text=feedback) # Update GUI
    
    # If feedback was just the list (not an error message), don't speak the whole list again.
    # Speaking is handled per-note above for the first few notes.
    if feedback in ["Could not access the notes directory.", "You have no notes."]:
        speak(feedback) # Speak error or "no notes" message

    if status_label: # Ensure GUI updates if it was a long list.
        status_label.winfo_toplevel().update_idletasks()


def handle_send_email_intent(command_text: str):
    """
    Handles the 'send_email' intent.

    Guides the user through providing recipient, subject, and body for the email,
    transcribing each part. Finally, saves the email draft using
    `email_module.draft_email`. Updates the GUI status label at each step and
    with the final outcome.

    Args:
        command_text: The original transcribed text that triggered this intent.
                      Currently unused.
    """
    global status_label
    
    # --- Get Recipient ---
    if status_label:
        status_label.config(text="Intent: Send Email. Who is the recipient?")
    speak("Who is the recipient?")
    print("Please say the recipient's email address:")
    recipient_text = listen_and_transcribe()
    if not recipient_text or (isinstance(recipient_text, str) and recipient_text.startswith("Google STT error:")):
        feedback = recipient_text or "I didn't catch the recipient. Please try sending the email again."
        print(feedback)
        speak(feedback)
        if status_label:
            status_label.config(text=feedback)
        return

    # --- Get Subject ---
    if status_label:
        status_label.config(text=f"Recipient: {recipient_text}. What's the subject?")
    speak("What is the subject?")
    print("Please say the subject:")
    subject_text = listen_and_transcribe()
    if not subject_text or (isinstance(subject_text, str) and subject_text.startswith("Google STT error:")):
        feedback = subject_text or "I didn't catch the subject. Please try sending the email again."
        print(feedback)
        speak(feedback)
        if status_label:
            status_label.config(text=feedback)
        return

    # --- Get Body ---
    if status_label:
        status_label.config(text=f"Subject: {subject_text}. What should the email say?")
    speak("What should the email say?")
    print("Please dictate the body of the email:")
    body_text = listen_and_transcribe()
    if not body_text or (isinstance(body_text, str) and body_text.startswith("Google STT error:")):
        feedback = body_text or "I didn't catch the email body. Please try sending the email again."
        print(feedback)
        speak(feedback)
        if status_label:
            status_label.config(text=feedback)
        return

    # --- Draft and Save Email ---
    if status_label:
        status_label.config(text="Saving email draft...")
    if draft_email(recipient_text, subject_text, body_text):
        feedback = "Email draft saved successfully."
    else:
        feedback = "Sorry, I couldn't save the email draft."
    
    print(feedback)
    speak(feedback)
    if status_label:
        status_label.config(text=feedback)

# --- Meeting Transcription Flow Functions ---
def continuous_transcription_loop():
    """
    Continuously listens for and transcribes speech during an active meeting.
    Appends transcribed segments to `current_meeting_transcript_parts` and
    the `MEETING_TEMP_FILE`. Stops when `is_meeting_recording_active` becomes False
    or if a "stop_meeting" command is detected in a transcribed segment.
    """
    # Ensure global state variables are accessible
    global is_meeting_recording_active, current_meeting_transcript_parts, status_label, root, MEETING_TEMP_FILE
    # Functions from other modules are imported at the top of main.py

    if not root: 
        print("Error: Tkinter root not initialized. Cannot run continuous transcription loop.")
        if is_meeting_recording_active: 
            is_meeting_recording_active = False 
        return

    # This initial status update and speak call are now in start_meeting_transcription_flow
    # to avoid repetition if the loop were structured to be re-entrant or restarted.
    # For this specific subtask, it might seem redundant but aligns with the prompt's flow.
    # if status_label:
    #    status_label.config(text="Meeting active. Transcribing continuously...")
    # speak("I'm now listening to the meeting.")
    
    try:
        # Open temp file in append mode. This creates the file if it doesn't exist.
        with open(MEETING_TEMP_FILE, "a", encoding="utf-8") as temp_f: # Added encoding as good practice
            while is_meeting_recording_active:
                if status_label: 
                    # Keep GUI responsive by processing its events before the blocking STT call
                    status_label.winfo_toplevel().update_idletasks() 
                
                print("Meeting loop: Listening for next segment...") # Console log
                # Call listen_and_transcribe with a longer phrase duration for meetings
                # The audio_handler.listen_and_transcribe has phrase_duration_limit with default 10.0
                segment_text = listen_and_transcribe(phrase_duration_limit=15.0) 
                
                if not is_meeting_recording_active: 
                    print("Meeting recording was stopped while listening for a segment.")
                    break 
                
                if segment_text:
                    # Check for STT error messages (e.g., network issues for Google STT)
                    if segment_text.startswith("Google STT error:") or segment_text.startswith("Could not reach Google"):
                        print(f"Meeting loop: STT Error: {segment_text}")
                        # Log and continue.
                    else:
                        # Successfully transcribed segment
                        print(f"Meeting loop: Transcribed: {segment_text}") 
                        current_meeting_transcript_parts.append(segment_text)
                        temp_f.write(segment_text + "\n") 
                        temp_f.flush() # Ensure segment is written to disk immediately.
                        
                        # Optional: Update GUI status with a snippet of the last transcribed segment.
                        # if status_label:
                        #     status_label.config(text=f"Last said: {segment_text[:40]}...")
                        
                        # Check for "stop meeting" command within the transcribed segment itself.
                        parsed_command_in_segment = parse_intent(segment_text.lower())
                        if parsed_command_in_segment == "stop_meeting":
                            speak("Stop meeting command detected within transcription.")
                            stop_meeting_transcription_flow() 
                            break 
                else:
                    # listen_and_transcribe returned None
                    print("Meeting loop: No speech detected or error in transcription for this segment.")
                    # Optionally, add a small delay here to prevent tight looping on continuous errors
                    # import time
                    # time.sleep(0.1) 

                # Crucial: Allow GUI to update and process other events
                if root: 
                    root.update() # Process Tkinter events

    except Exception as e:
        print(f"Error in continuous_transcription_loop: {e}")
        if status_label:
            status_label.config(text=f"Error during meeting: {e}") 
        if is_meeting_recording_active: 
            is_meeting_recording_active = False 
            stop_meeting_transcription_flow() # Attempt to save what was captured
    finally:
        # This block executes whether the loop finished normally or due to an exception.
        # stop_meeting_transcription_flow handles the temp file and final state.
        # If an error occurred and stop_meeting_transcription_flow was called, is_meeting_recording_active is False.
        # If this loop exited due to is_meeting_recording_active becoming False from elsewhere (e.g. direct stop button),
        # this ensures the state is consistent.
        if is_meeting_recording_active: 
             is_meeting_recording_active = False 
        
        # The prompt included a specific check for the temp file here, but
        # stop_meeting_transcription_flow now tries to recover from the temp file if
        # current_meeting_transcript_parts is empty, and then deletes it.
        # So, explicit handling here might be redundant or conflict.
        # if os.path.exists(MEETING_TEMP_FILE) and not current_meeting_transcript_parts:
        #     pass # stop_meeting_transcription_flow should handle this.

        print("Exited continuous_transcription_loop.")


def start_meeting_transcription_flow():
    """Initiates the meeting transcription process."""
    global is_meeting_recording_active, current_meeting_transcript_parts, status_label, root
    
    if not root:
        print("Cannot start meeting: Tkinter root not available.")
        speak("Error: Cannot start meeting due to a GUI issue.")
        if status_label:
            status_label.config(text="Error: GUI not ready for meeting.")
        return

    is_meeting_recording_active = True
    current_meeting_transcript_parts = [] # Clear any previous parts
    
    # Clear the temp file at the start of a new meeting
    try:
        with open(MEETING_TEMP_FILE, "w", encoding="utf-8") as temp_f: # Open in write mode to clear it
            temp_f.write("") 
        print(f"Cleared temp file: {MEETING_TEMP_FILE}")
    except Exception as e_clear:
        print(f"Error clearing temp file {MEETING_TEMP_FILE}: {e_clear}")
        # Proceed even if clearing fails, appending might still work or handle error in loop.

    speak("Meeting recording started. I will transcribe continuously. Say 'stop meeting' to end.")
    if status_label:
        status_label.config(text="Meeting recording active...")
    
    print("DEBUG: Meeting recording started. Transcript parts cleared.") # Console log
    
    # It's better to run the loop in a separate thread to avoid freezing the GUI
    # during the continuous_transcription_loop, especially the speak() calls.
    # However, for this iteration, we'll call it directly as per the prompt's structure.
    # A more advanced solution would use threading.Thread(target=continuous_transcription_loop).start()
    continuous_transcription_loop()

def stop_meeting_transcription_flow():
    """Stops the meeting transcription and saves the transcript."""
    global is_meeting_recording_active, current_meeting_transcript_parts, status_label, MEETING_TEMP_FILE
    
    # Ensure this is set to False first to stop any ongoing loops if they check this flag.
    is_meeting_recording_active = False 
    speak("Stopping meeting recording.")
    
    # Read from temp file first, in case the loop appended more than what's in current_meeting_transcript_parts
    # due to how parts are appended vs. when an error might occur.
    # For simplicity now, we'll rely on current_meeting_transcript_parts, assuming it's the primary source.
    # A more robust solution might merge or prioritize temp file content.
    
    # If current_meeting_transcript_parts is empty but temp file has content, use temp file.
    # This could happen if an error occurred after writing to temp_f but before appending to list.
    if not current_meeting_transcript_parts and os.path.exists(MEETING_TEMP_FILE):
        try:
            with open(MEETING_TEMP_FILE, "r", encoding="utf-8") as temp_f_read:
                # Read lines and strip newlines that were added during write
                current_meeting_transcript_parts = [line.strip() for line in temp_f_read if line.strip()]
            print(f"Recovered transcript from {MEETING_TEMP_FILE}")
        except Exception as e_read_temp:
            print(f"Error reading from temp file {MEETING_TEMP_FILE}: {e_read_temp}")
            # Proceed with whatever is in current_meeting_transcript_parts

    full_transcript = "\n".join(current_meeting_transcript_parts)
    
    if full_transcript:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_{timestamp}.txt"
        try:
            if not os.path.exists(NOTES_DIR): # Ensure notes directory exists
                os.makedirs(NOTES_DIR)
                print(f"Created directory for meeting transcripts: {NOTES_DIR}")

            filepath = os.path.join(NOTES_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(full_transcript)
            
            feedback = f"Meeting transcript saved as {filename} in '{NOTES_DIR}' directory."
        except Exception as e:
            feedback = f"Error saving meeting transcript: {e}"
    else:
        feedback = "No transcript content was recorded to save."
            
    print(feedback) # Console log
    speak(feedback)
    if status_label:
        status_label.config(text=feedback) # Update GUI
            
    current_meeting_transcript_parts = [] # Reset for next time
    
    # Clean up the temporary meeting file after attempting to save.
    if os.path.exists(MEETING_TEMP_FILE):
        try:
            os.remove(MEETING_TEMP_FILE)
            print(f"Cleaned up temp file: {MEETING_TEMP_FILE}")
        except Exception as e_remove:
            print(f"Error removing temp file {MEETING_TEMP_FILE}: {e_remove}")

    # Ensure GUI updates after all operations.
    if status_label: 
        status_label.winfo_toplevel().update_idletasks()


# --- Button Callback Function ---
def on_record_button_pressed():
    """
    Callback function executed when the "Push to Talk" button is pressed.

    Initiates audio listening and transcription. If successful, it parses the
    intent from the transcribed text and calls the appropriate handler function.
    Updates the GUI status label throughout the process.
    """
    global status_label, is_meeting_recording_active, root # Need is_meeting_recording_active and root
    
    # If a meeting is active, the button press should ideally not try to parse a new command
    # unless continuous_transcription_loop handles this (e.g. by being in a separate thread
    # and this button press is for a different purpose, or if the loop itself is triggered by button presses).
    # For now, the loop runs after "start meeting" and this button is the only input.
    # If meeting is active, this button press is effectively for the next segment OR a stop command.
    
    print("Record button pressed.") # Console log for debugging
    if status_label:
        # If not in meeting, show "Listening...". If in meeting, it's already showing "Meeting active..."
        # The continuous_transcription_loop will handle its own status updates.
        if not is_meeting_recording_active:
            status_label.config(text="Listening...") # Update GUI
        else:
            # During an active meeting, the button press contributes to the ongoing transcription
            # or could be a "stop meeting" command. The continuous loop handles this.
            # We might not need to change the status_label here if the loop does it.
            # However, if the loop is blocked on listen_and_transcribe, this provides feedback.
            status_label.config(text="Meeting: Capturing next segment...")


    if status_label:
        status_label.winfo_toplevel().update_idletasks()

    # If a meeting is active, the transcription is handled by the loop, which is initiated by start_meeting_transcription_flow.
    # The button press should not directly call listen_and_transcribe if the loop is supposed to be running.
    # This indicates a potential conflict in how the loop and button interact.
    # For this step, we assume the continuous_transcription_loop IS the primary listener during meetings.
    # The button press might be re-purposed or disabled during meetings in a more complex GUI.
    # OR, the loop itself is driven by button presses (segment by segment).
    # Given the current structure, let's assume the loop is running independently after "start meeting".
    # So, if a meeting is active, this button press is for a *new command* that might interrupt or affect the meeting.

    transcribed_text = listen_and_transcribe() # This is for general commands.

    if status_label: 
        status_label.winfo_toplevel().update_idletasks()

    if transcribed_text:
        if transcribed_text.startswith("Google STT error:") or transcribed_text.startswith("Could not reach Google"):
            feedback = transcribed_text 
            print(feedback)
            speak(feedback) 
            if status_label and not is_meeting_recording_active: # Avoid overwriting meeting status
                status_label.config(text=feedback)
        else:
            print(f"You said: {transcribed_text}") 
            if status_label and not is_meeting_recording_active:
                display_text = transcribed_text
                if len(transcribed_text) > 50:
                    display_text = transcribed_text[:47] + "..."
                status_label.config(text=f"Transcribed: {display_text}")
            
            intent = parse_intent(transcribed_text) 

            if intent == "start_meeting":
                if is_meeting_recording_active:
                    speak("Meeting recording is already active.")
                    if status_label: status_label.config(text="Meeting recording is already active.")
                else:
                    # This will call continuous_transcription_loop internally
                    start_meeting_transcription_flow() 
            elif intent == "stop_meeting":
                if not is_meeting_recording_active:
                    speak("No meeting recording is currently active.")
                    if status_label: status_label.config(text="No meeting recording is currently active.")
                else:
                    # This will set is_meeting_recording_active to False and break the loop.
                    stop_meeting_transcription_flow() 
            elif not is_meeting_recording_active: # Process other intents ONLY if no meeting is active
                if intent == "take_note":
                    speak("Okay, I will take a note.") 
                    handle_take_note_intent(transcribed_text)
                elif intent == "send_email":
                    speak("Okay, I will draft an email.") 
                    handle_send_email_intent(transcribed_text)
                elif intent == "list_notes":
                    speak("Okay, I will list your notes.") 
                    handle_list_notes_intent()
                elif intent is not None: # An intent was parsed but not one of the above (and no meeting)
                    feedback = "I'm not sure how to help with that."
                    print(feedback)
                    speak(feedback + " I heard you say: " + transcribed_text)
                    if status_label:
                        display_transcribed = transcribed_text[:30] + "..." if len(transcribed_text) > 30 else transcribed_text
                        status_label.config(text=feedback + f" You said: {display_transcribed}")
            elif is_meeting_recording_active and intent and intent not in ["start_meeting", "stop_meeting"]:
                # A meeting is active, but a different command was recognized.
                # This implies the continuous loop isn't capturing this, or this button press is interrupting.
                # For now, inform the user.
                speak(f"A meeting is currently being recorded. Please say 'stop meeting' to end it first if you want to issue other commands.")
                if status_label:
                    status_label.config(text=f"Meeting active. Command '{intent}' ignored. Say 'stop meeting' to end.")

    else: # Transcribed text is None
        if not is_meeting_recording_active: 
            feedback = "No speech detected or recognized by available engines."
            print(feedback)
            if status_label:
                status_label.config(text=feedback)

# --- Main Application Setup ---
def main_gui():
    """
    Sets up and runs the main Tkinter GUI for the Personal AI Agent.

    Initializes the main window, creates GUI elements (title, button, status label),
    and starts the Tkinter event loop.
    """
    global status_label # Allow this function to assign to the global status_label

    print("Personal AI Agent started (GUI Mode).")
    # speak("Personal AI Agent started.") # Optional: can be annoying on every startup

    # Initialize the main Tkinter window
    root = tk.Tk()
    root.title("Personal AI Agent")
    root.geometry("400x250") # Set initial window size (width x height)

    # Application Title Label
    title_label = tk.Label(root, text="Personal AI Agent", font=("Arial", 16, "bold"))
    title_label.pack(pady=(10,5)) # Add padding above and below the title
    
    # "Push to Talk" Button
    record_button = tk.Button(
        root, 
        text="Push to Talk", 
        command=on_record_button_pressed, # Function to call when clicked
        font=("Arial", 12), 
        width=20, height=2, 
        bg="#4CAF50", fg="white",  # Basic styling (background, foreground color)
        relief=tk.RAISED          # Button style
    )
    record_button.pack(pady=10) # Add padding around the button

    # Status Label (for feedback)
    # wraplength: ensures text wraps within the label width
    # justify: aligns multi-line text
    # height: reserves space for multiple lines of text
    # anchor: "nw" (north-west) aligns text to the top-left if label is larger than text
    status_label = tk.Label(
        root, 
        text="Press 'Push to Talk' to start.", 
        wraplength=380, 
        justify="left", 
        font=("Arial", 10), 
        height=7, 
        anchor="nw" 
    )
    status_label.pack(pady=(5,10), fill=tk.X, padx=10) # Fill available width, add padding

    # Start the Tkinter event loop. This keeps the window open and responsive.
    root.mainloop()

    print("Personal AI Agent stopped.")
    # speak("Personal AI Agent stopped.") # May not be heard if window closes too fast

if __name__ == "__main__":
    # This block runs when the script is executed directly.
    # main() # Old console-based main function (commented out)
    main_gui() # Run the GUI version of the application
