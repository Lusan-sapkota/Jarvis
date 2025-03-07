# import playsound
# import eel


# @eel.expose
# def playAssistantSound():
#     music_dir = "frontend\\assets\\audio\\start_sound.mp3"
#     playsound(music_dir)


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
    
    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME,"")
    query = query.replace("open","")
    query.lower()
    
    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute( 
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results != 0):
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results == 0): 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results != 0):
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")


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


def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="backend/cookie.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response

# Create a global lock for TTS operations
tts_lock = threading.Lock()

# Replace the pyttsx3 speak function with a more stable approach for Linux
def speak(text):
    """Use espeak directly via subprocess for more stability"""
    with tts_lock:  # Ensure only one speech command runs at a time
        try:
            # Use espeak directly via command line
            subprocess.run(['espeak', '-v', 'en+m3', text], 
                          check=True, 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            # Small delay to ensure speech is complete
            time.sleep(0.1)
        except Exception as e:
            print(f"Error in speak function: {e}")
            import traceback
            traceback.print_exc()