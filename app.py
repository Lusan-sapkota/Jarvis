import os
import sys
import eel
import time
import threading
import traceback
from backend.auth import recoganize
from backend.feature import (
    chatBot, 
    play_assistant_sound, 
    enter_sleep_mode, 
    exit_sleep_mode,
    get_sleep_status, 
    openCommand,
    hotword
)
from backend.command import speak, takecommand
from backend.db import initialize_linux_commands
import speech_recognition as sr

# Initialize Eel
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
print(f"Initializing Eel with frontend path: {frontend_path}")
eel.init(frontend_path)

# Flag to keep the main loop running
keep_running = True

# Track if authentication has already been completed
authentication_done = False

@eel.expose
def init():
    """Initialize the application after frontend loads"""
    global authentication_done
    print("Init function called from frontend")
    
    # Check if authentication has already been done to prevent duplicate processing
    if authentication_done:
        print("Authentication already completed, skipping...")
        return
        
    eel.hideLoader()
    try:
        # Face recognition
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            print("Face recognized successfully")
            speak("Face recognized successfully")
            
            # Mark authentication as complete
            authentication_done = True
            
            # Play startup sound
            try:
                play_assistant_sound()
            except Exception as e:
                print(f"Error playing startup sound: {e}")
            
            # Update UI
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            
            # Wait before showing main interface
            time.sleep(1.5)
            
            try:
                print("Showing main interface...")
                # Call the JavaScript function we defined
                eel.showMainInterface()
                print("Main interface should be visible now")
                
                # Final message
                speak("I am ready for your commands")
            except Exception as e:
                print(f"Error showing main interface: {e}")
                traceback.print_exc()
        else:
            print("Face not recognized")
            speak("Face not recognized. Please try again")
    except Exception as e:
        print(f"Error during initialization: {e}")
        traceback.print_exc()

@eel.expose
def toggle_sleep_mode():
    """Toggle sleep mode on/off"""
    current_status = get_sleep_status()
    if current_status:
        exit_sleep_mode()
    else:
        enter_sleep_mode()
    return not current_status

@eel.expose
def process_command(command):
    """Process user commands from the UI"""
    print(f"Received command: {command}")
    
    if get_sleep_status() and not ("wake up" in command.lower() or "wakeup" in command.lower()):
        response = "I'm currently in sleep mode. Say 'wake up' to activate me."
        # Make sure to update the UI before returning
        eel.receiverText(response)
        return response
    
    try:
        # First check for wake command
        if get_sleep_status() and ("wake up" in command.lower() or "wakeup" in command.lower()):
            exit_sleep_mode()
            response = "I'm awake and ready to assist you."
            eel.receiverText(response)
            return response
        
        # Check for sleep command
        if "sleep" in command.lower() or "go to sleep" in command.lower():
            enter_sleep_mode()
            response = "Sleep mode activated"
            eel.receiverText(response)
            return response
        
        # Check for open command
        if "open" in command.lower():
            app_name = command.lower().replace("open", "").strip()
            if app_name:
                openCommand(command)
                response = f"Opening {app_name}"
                eel.receiverText(response)
                return response
        
        # For all other commands, use chatBot
        response = chatBot(command)
        # Explicitly update the UI with the response
        eel.receiverText(response)
        return response
    except Exception as e:
        print(f"Error processing command: {e}")
        error_message = "I'm sorry, I encountered an error processing your command."
        speak(error_message)
        eel.receiverText(error_message)
        traceback.print_exc()
        return error_message

@eel.expose
def listen_for_command():
    """Listen for voice command using microphone"""
    try:
        query = takecommand()
        if query:
            # Process the recognized command
            response = process_command(query)
            return query
        return ""
    except Exception as e:
        print(f"Error in voice recognition: {e}")
        traceback.print_exc()
        if not get_sleep_status():
            speak("There was an error with the voice recognition system.")
        return ""

def open_browser():
    """Open the browser with the application URL"""
    url = "http://localhost:8000/index.html"
    try:
        print(f"Opening browser at: {url}")
        if sys.platform == "win32":
            os.system(f'start msedge.exe --app="{url}"')
        elif sys.platform == "darwin":
            os.system(f'open "{url}"')
        else:
            os.system(f'xdg-open "{url}"')
    except Exception as e:
        print(f"Error opening browser: {e}")

# Start the application
if __name__ == "__main__":
    try:
        # Initialize database
        initialize_linux_commands()
        
        # Start hotword detection in background
        hotword_thread = threading.Thread(target=hotword, daemon=True)
        hotword_thread.start()
        
        # Open browser
        threading.Timer(1.0, open_browser).start()
        
        # Start Eel
        print("Starting Eel server...")
        eel.start("index.html", mode=None, host="localhost", port=8000, block=True)
    except KeyboardInterrupt:
        print("Keyboard interrupt received, shutting down...")
        keep_running = False
    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
    finally:
        print("Application terminated")