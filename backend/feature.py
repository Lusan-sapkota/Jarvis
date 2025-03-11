from compileall import compile_path
import os
import re
import sys
import pyttsx3
from shlex import quote
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat 
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3
import threading

from backend.helper import extract_yt_term, remove_words
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()
# Initialize pygame mixer
pygame.mixer.init()

# Define the function to play sound
@eel.expose
def play_assistant_sound():
    sound_file = r"/home/lusan/Documents/Jarvis/frontend/assets/audio/start_sound.mp3" # Change the path to your sound file
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    
# Import necessary libraries 
import os
import re
import sys
import pyttsx3
import struct
import subprocess
import time
import webbrowser
import eel
from hugchat import hugchat 
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from backend.command import speak
from backend.config import ASSISTANT_NAME
import sqlite3
import threading
import wikipedia
import json
import requests
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

# Initialize Wikipedia language
wikipedia.set_lang("en")

# Initialize sleep mode
sleep_mode = False

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Initialize pygame mixer
pygame.mixer.init()

# Updated openCommand for Linux
def openCommand(query):
    query = query.replace(ASSISTANT_NAME,"")
    query = query.replace("open","")
    query = query.lower().strip()
    
    # Dictionary of common Linux applications and their commands
    linux_apps = {
        "code": ["code", "code ."],
        "vscode": ["code", "code ."],
        "visual studio code": ["code", "code ."],
        "chrome": ["google-chrome", "google-chrome"],
        "google chrome": ["google-chrome", "google-chrome"],
        "firefox": ["firefox", "firefox"],
        "android studio": ["studio", "/opt/android-studio/bin/studio.sh"],
        "terminal": ["gnome-terminal", "gnome-terminal"],
        "files": ["nautilus", "nautilus"],
        "file manager": ["nautilus", "nautilus"],
        "calculator": ["gnome-calculator", "gnome-calculator"],
        "text editor": ["gedit", "gedit"],
        "spotify": ["spotify", "spotify"],
        "discord": ["discord", "discord"],
        "slack": ["slack", "slack"],
        "vlc": ["vlc", "vlc"],
        "obs": ["obs", "obs"]
    }
    
    app_name = query.strip()

    if app_name != "":
        try:
            # First try the database lookup
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if results and len(results) > 0:
                speak("Opening " + app_name)
                subprocess.Popen(results[0][0], shell=True)
            
            # Then try web commands
            elif results and len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if results and len(results) > 0:
                    speak("Opening " + app_name)
                    webbrowser.open(results[0][0])
                
                # Then try our predefined Linux apps dictionary
                elif app_name in linux_apps:
                    speak("Opening " + app_name)
                    try:
                        subprocess.Popen(linux_apps[app_name][1], shell=True)
                    except Exception as e:
                        print(f"Error opening application: {e}")
                        speak("Failed to open " + app_name)
                
                # Finally try just launching the app name directly
                else:
                    speak("Opening " + app_name)
                    try:
                        subprocess.Popen(app_name, shell=True)
                    except Exception as e:
                        print(f"Error opening application: {e}")
                        speak("Sorry, I couldn't find " + app_name)
        except Exception as e:
            print(f"Error in openCommand: {e}")
            speak("Something went wrong while opening " + app_name)

# Sleep mode functions
@eel.expose
def enter_sleep_mode():
    global sleep_mode
    sleep_mode = True
    speak("Entering sleep mode. Say 'wake up' to activate me again.")
    eel.DisplayMessage("Sleeping...")
    return sleep_mode

@eel.expose
def exit_sleep_mode():
    global sleep_mode
    sleep_mode = False
    current_hour = time.localtime().tm_hour
    
    if current_hour < 12:
        greeting = "Good morning!"
    elif current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
        
    speak(f"{greeting} I'm back online and ready to assist you.")
    eel.DisplayMessage("Awake and listening...")
    return sleep_mode

# Enhanced chatBot with Wikipedia and Gemini API
def chatBot(query):
    global sleep_mode
    
    # Handle sleep and wake up commands
    if "sleep" in query.lower() or "go to sleep" in query.lower():
        return enter_sleep_mode()
        
    if sleep_mode and ("wake up" in query.lower() or "wakeup" in query.lower()):
        return exit_sleep_mode()
        
    # If in sleep mode, ignore other commands
    if sleep_mode:
        print("Currently in sleep mode. Say 'wake up' to activate.")
        return None
        
    # Handle built-in commands
    if "time" in query.lower():
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        response = f"The current time is {current_time}"
        speak(response)
        return response
        
    elif "date" in query.lower():
        from datetime import datetime
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        response = f"Today is {current_date}"
        speak(response)
        return response
        
    elif "hello" in query.lower() or "hi" in query.lower() or "hey" in query.lower():
        import random
        greetings = [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! I'm listening. What do you need?",
            "Greetings! How may I assist you?"
        ]
        response = random.choice(greetings)
        speak(response)
        return response
    
    # Try Wikipedia search
    try:
        print("Searching Wikipedia...")
        # Only use Wikipedia for search-like queries
        if any(word in query.lower() for word in ["what is", "who is", "define", "explain"]):
            search_term = query.lower()
            for prefix in ["what is", "who is", "define", "explain"]:
                search_term = search_term.replace(prefix, "").strip()
                
            results = wikipedia.summary(search_term, sentences=2)
            response = f"According to Wikipedia: {results}"
            print(response)
            speak(response)
            return response
        else:
            raise ValueError("Not a knowledge query")
    except Exception as wiki_error:
        print(f"Wikipedia error: {wiki_error}")
        
        # Try Gemini API
        try:
            print("Using Gemini API...")
            # Get API key from environment
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            
            if not gemini_api_key:
                # Create a helpful response if API key not found
                response = "I couldn't find information about that. To enable AI responses, please set up a Gemini API key in the .env file."
                speak(response)
                return response
            
            # Set up Gemini API request
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {
                "Content-Type": "application/json",
            }
            
            data = {
                "contents": [{"parts": [{"text": query}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 800,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            # Make the API request
            response = requests.post(
                f"{url}?key={gemini_api_key}",
                headers=headers,
                json=data
            )
            
            # Process the response
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                speak(text_response)
                return text_response
            else:
                fallback_response = "I don't have enough information to answer that question properly."
                speak(fallback_response)
                return fallback_response
                
        except Exception as gemini_error:
            print(f"Gemini API error: {gemini_error}")
            
            # Provide a good fallback response
            final_response = "I'm sorry, I couldn't process your request. Please check your internet connection and try again."
            speak(final_response)
            return final_response

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


# Updated hotword detection function

def hotword():
    """
    Listen for hotword with improved error handling
    """
    try:
        print("Initializing hotword detection...")
        
        # Import necessary libraries
        import time
        import struct
        import numpy as np
        
        # Create a directory for hotword files if it doesn't exist
        hotword_dir = os.path.join("backend", "hotword")
        if not os.path.exists(hotword_dir):
            os.makedirs(hotword_dir)
            print(f"Created hotword directory at {hotword_dir}")
            
        # Check if we have the porcupine library
        try:
            import pvporcupine
        except ImportError:
            print("Porcupine library not found. Please install with: pip install pvporcupine")
            print("Running in fallback mode - hotword detection disabled.")
            # Keep the process alive
            while True:
                time.sleep(5)
            return
            
        # Check if we have pyaudio
        try:
            import pyaudio
        except ImportError:
            print("PyAudio not found. Please install with: pip install pyaudio")
            print("Running in fallback mode - hotword detection disabled.")
            # Keep the process alive
            while True:
                time.sleep(5)
            return
        
        # Create a default keyword file using built-in "jarvis" keyword
        print("Attempting to use built-in 'jarvis' keyword")
        
        # Try to initialize Porcupine with built-in keyword
        try:
            # We'll use the built-in "jarvis" keyword that comes with Porcupine
            porcupine = pvporcupine.create(keywords=["jarvis"])
            print("Porcupine initialized with built-in 'jarvis' keyword")
        except Exception as e:
            print(f"Failed to initialize Porcupine with built-in keyword: {e}")
            print("You may need to get an access key from Picovoice")
            print("Running in fallback mode - hotword detection disabled")
            # Keep the process alive
            while True:
                time.sleep(5)
            return
                
        # Initialize PyAudio for microphone access
        p = pyaudio.PyAudio()
        
        try:
            # Open audio stream
            stream = p.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length
            )
            
            print("Audio stream opened successfully")
            print("Hotword detection is active - say 'Jarvis' to activate")
            
            # Main detection loop
            while True:
                # Read audio frame
                pcm = stream.read(porcupine.frame_length)
                pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)
                
                # Process with Porcupine
                keyword_index = porcupine.process(pcm_unpacked)
                
                # Hotword detected
                if keyword_index >= 0:
                    print("Hotword 'Jarvis' detected!")
                    # Play activation sound
                    try:
                        threading.Thread(target=play_activation_sound).start()
                    except:
                        pass
                    
                    # Trigger the assistant response
                    try:
                        threading.Thread(target=speak, args=("Yes, how can I help you?",)).start()
                    except:
                        pass
                
                # Small delay to prevent high CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            print(f"Error in hotword detection: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up resources
            if 'stream' in locals() and stream:
                stream.close()
            if 'porcupine' in locals() and porcupine:
                porcupine.delete()
            p.terminate()
                
    except Exception as e:
        print(f"Critical error in hotword function: {e}")
        import traceback
        traceback.print_exc()
    
    print("Hotword detection terminated")
    
    # Keep the process alive in case of errors
    print("Keeping hotword process alive despite errors...")
    while True:
        time.sleep(5)


def play_activation_sound():
    """Play a sound when the hotword is detected"""
    try:
        # First check if we have the sound file
        sound_path = os.path.join('assets', 'sounds', 'activation.mp3')
        
        # If not found, check alternative location
        if not os.path.exists(sound_path):
            sound_path = os.path.join('assets', 'sounds', 'startup.mp3')
            
        # If still not found, return silently
        if not os.path.exists(sound_path):
            print(f"Warning: No activation sound file found")
            return
            
        # Try different playback methods
        try:
            # First try paplay (PulseAudio)
            subprocess.run(['paplay', sound_path], 
                          check=False,
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
        except:
            try:
                # Try pygame
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except:
                print("Failed to play activation sound")
                
    except Exception as e:
        print(f"Error playing activation sound: {e}")


def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
    
def whatsApp(Phone, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)


# Create a global lock for TTS operations
tts_lock = threading.Lock()

# Add function to expose sleep status to other modules
@eel.expose
def get_sleep_status():
    """Return current sleep mode status"""
    global sleep_mode
    return sleep_mode

def feature_process_command(query):  # Renamed from process_command
    """Main function to process user commands"""
    global sleep_mode
    
    # Handle sleep and wake up commands
    if "sleep" in query.lower() or "go to sleep" in query.lower():
        return enter_sleep_mode()
        
    if sleep_mode and ("wake up" in query.lower() or "wakeup" in query.lower()):
        return exit_sleep_mode()
        
    # If in sleep mode, ignore other commands
    if sleep_mode:
        print("Currently in sleep mode. Say 'wake up' to activate.")
        return None
    
    # Determine what type of command this is
    if "open" in query.lower():
        openCommand(query)
        return "Command executed"
        
    if "play" in query.lower() and "youtube" in query.lower():
        PlayYoutube(query)
        return "Playing video on YouTube"
        
    if any(x in query.lower() for x in ["call", "message", "whatsapp"]):
        # Handle contact commands
        if "call" in query.lower():
            mobile, name = findContact(query)
            if mobile != 0:
                whatsApp(mobile, "", "call", name)
            return "Call initiated"
        elif "message" in query.lower() or "whatsapp" in query.lower():
            mobile, name = findContact(query)
            if mobile != 0:
                # Extract message content - this is a simplification
                message = "Hello" # You would extract the actual message here
                whatsApp(mobile, message, "message", name)
            return "Message sent"
    
    # For general queries, use the chatBot
    return chatBot(query)

# Removed @eel.expose decorator to fix name collision with app.py
def process_command(query):
    """Main function to process user commands - this is a wrapper for app.py integration"""
    # Pass the query to the existing process_command in app.py
    # The actual implementation is in app.py, this is just to fix the import error
    try:
        # For simple built-in commands
        if "sleep" in query.lower() or "go to sleep" in query.lower():
            return enter_sleep_mode()
        
        if sleep_mode and ("wake up" in query.lower() or "wakeup" in query.lower()):
            return exit_sleep_mode()
        
        # For general queries, use chatBot
        return chatBot(query)
    except Exception as e:
        print(f"Error in feature.process_command: {e}")
        return "Sorry, I encountered an error processing that command."