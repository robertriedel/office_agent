# Personal AI Agent

This is a voice-controlled personal AI agent capable of taking notes, drafting emails, and listing existing notes.

## Setup and Prerequisites

### 1. Python Environment
Ensure you have Python 3 installed (version 3.10 or newer recommended).

### 2. Tkinter for GUI
The graphical user interface requires Tkinter.
*   **Debian/Ubuntu Linux:**
    ```bash
    sudo apt-get update
    sudo apt-get install python3-tk
    ```
*   **Fedora Linux:**
    ```bash
    sudo dnf install python3-tkinter
    ```
*   **Windows:** Tkinter is usually included with the standard Python installer. If not, ensure it's selected during installation or re-run the Python installer to add it.
*   **macOS:** Tkinter is usually included with the Python installation from python.org. If you are using a system Python, you might need to install it separately (e.g., via Homebrew `brew install python-tk`).

### 3. Python Dependencies
The project uses several Python libraries. Install them using pip:
```bash
pip install -r requirements.txt
```
This will install packages like `SpeechRecognition`, `pyttsx3`, `PyAudio`, `pocketsphinx`, etc.

*(Note: `openai-whisper` is listed in `requirements.txt` for potential future use but its installation might fail in resource-constrained environments due to its large dependencies like `torch`.)*

## Running the Agent
Once prerequisites are met, you can run the agent from the `personal_ai_agent` directory:
```bash
python3 main.py
```
A GUI window will appear. Click the "Push to Talk" button to issue voice commands.

## Features
*   **Take Notes:** Say "take a note", and the agent will prompt you for the content. Notes are saved in the `notes/` directory.
*   **Draft Emails:** Say "draft an email", and the agent will guide you through recipient, subject, and body. Drafts are saved in the `drafts/` directory.
*   **List Notes:** Say "list my notes", and the agent will show and speak a list of your saved notes.
*   **Search Notes:** Say "search my notes" and specify a keyword to find notes containing that text.
*   **Help:** Say "help" to hear a summary of available commands.

## Speech Recognition
*   The agent primarily uses CMU Sphinx for offline speech-to-text.
*   If Sphinx cannot understand the audio, it will attempt to use Google Speech Recognition as a fallback (requires an internet connection).
