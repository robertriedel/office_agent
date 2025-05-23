"""
Handles audio input (Speech-to-Text) and output (Text-to-Speech)
for the Personal AI Agent.

This module initializes the TTS engine (pyttsx3) and provides functions
to speak given text and to listen for user voice input, transcribing it
into text using speech recognition libraries.
"""
import pyttsx3
import speech_recognition as sr

# --- TTS Engine Initialization and Configuration ---
engine = None  # Global TTS engine instance
try:
    engine = pyttsx3.init()
    if engine:
        # --- TTS Configuration ---
        # The following sections are for configuring the TTS voice, rate, and volume.
        # Errors during configuration are caught to prevent application startup failure.

        # Example: Listing available voices (useful for debugging or selection)
        # try:
        #     voices = engine.getProperty('voices')
        #     print("Available TTS Voices:")
        #     for voice in voices:
        #         print(f"  ID: {voice.id}, Name: {voice.name}, Langs: {voice.languages}, Gender: {voice.gender}")
        #     current_voice_id = engine.getProperty('voice')
        #     print(f"Current default voice ID: {current_voice_id}")
        #     # To select a specific voice:
        #     # engine.setProperty('voice', voices[0].id) # Selects the first available voice
        # except Exception as e_voice:
        #     print(f"Error getting/setting voice properties: {e_voice}")

        # Adjust speech rate
        try:
            current_rate = engine.getProperty('rate')
            print(f"Default TTS rate: {current_rate}")
            engine.setProperty('rate', 150)  # Standard speaking rate, adjust as needed
            print(f"New TTS rate: {engine.getProperty('rate')}")
        except Exception as e_rate:
            print(f"Error setting TTS rate: {e_rate}")

        # Adjust volume (0.0 to 1.0)
        try:
            current_volume = engine.getProperty('volume')
            print(f"Default TTS volume: {current_volume}")
            engine.setProperty('volume', 0.9)  # Set volume to 90%
            print(f"New TTS volume: {engine.getProperty('volume')}")
        except Exception as e_volume:
            print(f"Error setting TTS volume: {e_volume}")
    else:
        # This case might occur if pyttsx3.init() itself returns None or fails silently.
        print("TTS engine could not be initialized by pyttsx3.init().")

except Exception as e_init:
    # Catch any other unexpected errors during pyttsx3 initialization.
    print(f"Fatal error initializing pyttsx3 or setting properties: {e_init}")
    engine = None # Ensure engine is None if initialization failed catastrophically.

def speak(text: str):
    """
    Converts the given text to speech using the initialized pyttsx3 engine.

    Args:
        text: The string to be spoken.
    """
    if not engine:
        print("TTS engine not initialized or failed during setup. Cannot speak.")
        return
    try:
        print(f"TTS: Speaking '{text}'")
        engine.say(text)
        engine.runAndWait()  # Blocks while the text is being spoken
    except Exception as e_speak:
        print(f"Error in speak function: {e_speak}")

def listen_and_transcribe() -> str | None:
    """
    Listens for audio input from the microphone and transcribes it to text.

    It uses speech_recognition library and attempts transcription in the following order:
    1. CMU Sphinx (offline)
    2. Google Speech Recognition (online, as a fallback)

    Returns:
        The transcribed text as a string if successful.
        A specific error message string if Google STT fails due to a request error.
        None if speech is not detected, cannot be understood by any STT engine,
        or if an unexpected error occurs during the process.

    Args:
        phrase_duration_limit (float | None): The maximum number of seconds that
                                              `recognizer.listen()` will wait for a phrase to complete
                                              before timing out. Default is 10 seconds.
    """
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    transcribed_text = None  # Initialize transcribed_text to None

    # Capture audio from the microphone
    with microphone as source:
        print("Listening... (adjusting for ambient noise)")
        try:
            # Adjust for ambient noise to improve recognition accuracy.
            # Duration of 1 second is usually sufficient.
            recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e_adjust:
            print(f"Error adjusting for ambient noise: {e_adjust}")
            # Continue even if adjustment fails, recognition might still work.

        print("Ready to listen for command...")
        try:
            # Listen for the first phrase and extract it into audio data.
            # timeout: max seconds recognizer will wait for a phrase to start.
            # phrase_time_limit: max seconds a phrase can be.
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=phrase_duration_limit or 10.0)
        except sr.WaitTimeoutError:
            print("No speech detected within the timeout period.")
            return None
        except Exception as e_listen:
            print(f"Error during listening: {e_listen}")
            return None
    
    # Attempt CMU Sphinx STT (Offline) if audio was captured
    if audio_data:
        try:
            print("Recognizing with Sphinx STT...")
            transcribed_text = recognizer.recognize_sphinx(audio_data)
            print(f"Transcribed with Sphinx: {transcribed_text}")
        except sr.UnknownValueError:
            # Sphinx could not understand the audio.
            print("Sphinx could not understand audio.")
            transcribed_text = None # Ensure text is None to trigger fallback
        except sr.RequestError as e_sphinx:
            # This typically means pocketsphinx is not installed or configured correctly.
            print(f"Sphinx error; {e_sphinx}. Ensure pocketsphinx is installed.")
            transcribed_text = None # Ensure text is None
        except Exception as e_sphinx_other:
            print(f"An unexpected error occurred with Sphinx: {e_sphinx_other}")
            transcribed_text = None

    # Fallback to Google Speech Recognition (Online) if Sphinx failed and audio was captured
    if not transcribed_text and audio_data:
        try:
            print("Recognizing with Google STT...")
            transcribed_text = recognizer.recognize_google(audio_data)
            print(f"Transcribed with Google: {transcribed_text}")
        except sr.UnknownValueError:
            # Google could not understand the audio.
            print("Google Speech Recognition could not understand audio.")
            transcribed_text = None # Explicitly set to None
        except sr.RequestError as e_google:
            # API was unreachable or unresponsive.
            error_message = f"Google STT error: Could not request results; {e_google}"
            print(error_message)
            return error_message # Return specific error message for main.py to handle
        except Exception as e_google_other:
            print(f"An unexpected error occurred with Google STT: {e_google_other}")
            transcribed_text = None # Explicitly set to None
            
    # Final checks
    if not audio_data:
        # This case should ideally be caught by listen errors, but as a safeguard:
        print("No audio captured, cannot transcribe.")
        return None

    if not transcribed_text:
        # This means all attempted STT engines failed to produce a result.
        print("STT failed with all available engines or no audio captured initially.")
        return None # General failure if no specific Google error was returned
        
    return transcribed_text
