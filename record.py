# Start by making sure the `assemblyai` package is installed.
# If not, you can install it by running the following command:
# pip install -U assemblyai
#
# Then, make sure you have PyAudio installed: https://pypi.org/project/PyAudio/
#
# Note: Some macOS users might need to use `pip3` instead of `pip`.

import assemblyai as aai
import signal
import threading
import time
import os
from dotenv import load_dotenv
import curses
import logging

# Load environment variables from .env file
load_dotenv()

# Read API key from environment variable
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

sentences = []
current_sentence = ""
transcript_lock = threading.Lock()
stdscr = None

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def init_curses():
    global stdscr
    logging.debug("Initializing curses")
    try:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        curses.curs_set(0)
        logging.debug("Curses initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing curses: {e}")
        raise

def cleanup_curses():
    if stdscr:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

def on_open(session_opened: aai.RealtimeSessionOpened):
    "This function is called when the connection has been established."
    logging.debug(f"Session opened with ID: {session_opened.session_id}")
    print("Session ID:", session_opened.session_id)
    threading.Thread(target=write_transcript_to_file, daemon=True).start()

def on_data(transcript: aai.RealtimeTranscript):
    global sentences, current_sentence, stdscr
    logging.debug(f"Received transcript: {transcript.text}")
    if not transcript.text:
        return

    with transcript_lock:
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            sentences.append(transcript.text)
            current_sentence = ""
            update_display()
        else:
            current_sentence = transcript.text
            update_display()

def wrap_text(text, width):
    """Split text into lines that fit within the given width."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def update_display():
    global sentences, current_sentence, stdscr
    if not stdscr:
        return

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Display final sentences at the top
    y = 0
    for sentence in sentences:
        wrapped_lines = wrap_text(sentence, width - 1)
        for line in wrapped_lines:
            if y < height - 2:  # Leave space for current sentence
                stdscr.addstr(y, 0, line)
                y += 1
            else:
                break
        if y >= height - 2:
            break

    # Display current sentence at the bottom
    wrapped_current = wrap_text(current_sentence, width - 1)
    for i, line in enumerate(wrapped_current):
        if height - len(wrapped_current) + i < height:
            stdscr.addstr(height - len(wrapped_current) + i, 0, line)

    stdscr.refresh()

def write_transcript_to_file():
    global sentences, current_sentence
    while True:
        with transcript_lock:
            full_transcript = "\n".join(sentences + [current_sentence])
        with open("transcript.txt", "w") as f:
            f.write(full_transcript)
        time.sleep(1)  # Update file every second

def on_error(error: aai.RealtimeError):
    "This function is called when the connection has been closed."

    print("An error occured:", error)

def on_close():
    "This function is called when the connection has been closed."

    print("Closing Session")

def signal_handler(sig, frame):
    print("\nStopping transcription...")
    transcriber.close()
    cleanup_curses()
    exit(0)

transcriber = aai.RealtimeTranscriber(
    on_data=on_data,
    on_error=on_error,
    sample_rate=44_100,
    on_open=on_open, # optional
    on_close=on_close, # optional
)

# Start the connection
transcriber.connect()

# Open a microphone stream
microphone_stream = aai.extras.MicrophoneStream()

# Set up signal handler for CTRL+C
signal.signal(signal.SIGINT, signal_handler)

try:
    logging.debug("Starting transcription")
    init_curses()
    transcriber.stream(microphone_stream)
except Exception as e:
    logging.error(f"Error during transcription: {e}")
    print(f"An error occurred: {e}")
finally:
    logging.debug("Cleaning up")
    transcriber.close()
    cleanup_curses()
    print("Transcription stopped.")
