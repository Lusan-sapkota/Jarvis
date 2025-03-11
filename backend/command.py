import time
import pyttsx3
import speech_recognition as sr
import eel
import sys
import threading
import subprocess
import traceback
from backend.config import ASSISTANT_NAME

# Create a global lock for TTS operations
tts_lock = threading.Lock()

def speak(text):
    """
    Text-to-speech function that works well across platforms
    """
    text = str(text)
    try:
        # First display the message in the UI
        eel.DisplayMessage(text)
        
        with tts_lock:  # Ensure only one speech command runs at a time
            if sys.platform in ['linux', 'darwin']:
                # Use espeak directly via subprocess for Linux/Mac
                try:
                    subprocess.run(['espeak', '-v', 'en+m3', text], 
                                check=True, 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
                except:
                    # Fallback to pyttsx3 if espeak fails
                    engine = pyttsx3.init('espeak')
                    voices = engine.getProperty('voices')
                    engine.setProperty('voice', voices[2].id if len(voices) > 2 else voices[0].id)
                    engine.setProperty('rate', 174)
                    engine.say(text)
                    engine.runAndWait()
            else:
                # Use pyttsx3 for Windows
                engine = pyttsx3.init('sapi5')
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[2].id if len(voices) > 2 else voices[0].id)
                engine.setProperty('rate', 174)
                engine.say(text)
                engine.runAndWait()
                
        # Send the text to the UI
        eel.receiverText(text)
        
    except Exception as e:
        print(f"Error in speak function: {str(e)}")
        traceback.print_exc()

def takecommand(timeout=10, phrase_time_limit=8):
    """
    Listen for a voice command with configurable timeouts
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("I'm listening...")
        eel.DisplayMessage("I'm listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.")
            return None

    try:
        print("Recognizing...")
        eel.DisplayMessage("Recognizing...")
        query = r.recognize_google(audio, language='en-US')
        print(f"User said: {query}\n")
        eel.DisplayMessage(query)
        
        # Don't speak the query back to the user - removed to improve UX
        # speak(query)
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from speech recognition service; {e}")
        return None
    except Exception as e:
        print(f"Error in speech recognition: {str(e)}\n")
        return None

    return query.lower() if query else None

@eel.expose
def takeAllCommands(message=None):
    """
    Process commands from either voice or text input
    """
    # Get the command from voice or text
    if message is None:
        query = takecommand()  # If no message is passed, listen for voice input
        if not query:
            return  # Exit if no query is received
        print(f"Voice command: {query}")
        eel.senderText(query)
    else:
        query = message.lower()  # If there's a message, use it
        print(f"Text command: {query}")
        eel.senderText(query)
    
    try:
        # Process the command
        from backend.feature import process_command
        result = process_command(query)
        
        # Show the hood after processing is complete
        eel.ShowHood()
        
        return result
    except Exception as e:
        print(f"Error processing command: {str(e)}")
        traceback.print_exc()
        speak("Sorry, something went wrong.")
        eel.ShowHood()
        return None
