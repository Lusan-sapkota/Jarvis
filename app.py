import os
import sys
import eel
import time
import threading
import traceback
from backend.auth import recoganize
from backend.feature import *
import speech_recognition as sr
import json
import os.path
import requests
from pathlib import Path

# Initialize Eel
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
print(f"Initializing Eel with frontend path: {frontend_path}")
eel.init(frontend_path)

# Flag to keep the main loop running
keep_running = True

# Track if authentication has already been completed
authentication_done = False

def speak_safely(text):
    """Safe wrapper for speak function"""
    try:
        print(f"Speaking: '{text}'")
        speak(text)
    except Exception as e:
        print(f"Error in speak: {e}")

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
            speak_safely("Face recognized successfully")
            
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
            speak_safely("Welcome to Your Assistant")
            eel.hideStart()
            
            # Wait before showing main interface
            time.sleep(1.5)
            
            try:
                print("Showing main interface...")
                # Call the JavaScript function we defined
                eel.showMainInterface()
                print("Main interface should be visible now")
                
                # Final message
                speak_safely("I am ready for your commands")
            except Exception as e:
                print(f"Error showing main interface: {e}")
                traceback.print_exc()
        else:
            print("Face not recognized")
            speak_safely("Face not recognized. Please try again")
    except Exception as e:
        print(f"Error during initialization: {e}")
        traceback.print_exc()

# Add this function to handle Hugging Face API calls
def get_huggingface_response(query):
    """Get response from Hugging Face API with error handling"""
    try:
        # Check if cookie file exists
        cookie_path = os.path.join('backend', 'cookie.json')
        if not os.path.exists(cookie_path):
            print("Creating empty cookie.json file")
            os.makedirs(os.path.dirname(cookie_path), exist_ok=True)
            with open(cookie_path, 'w') as f:
                json.dump([{
                    "name": "hf-chat",
                    "value": "placeholder",
                    "domain": "huggingface.co",
                    "path": "/chat",
                    "expires": -1,
                    "httpOnly": False,
                    "secure": True
                }], f)
            print(f"Created cookie file at {cookie_path}")
            
        # Try direct API approach instead of huggingchat library
        # This is more stable and doesn't rely on the cookie file
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
            headers={"Authorization": "//"},  # Replace with your API key
            json={"inputs": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and result:
                return result[0].get('generated_text', "I'm not sure how to respond to that.")
            return "I'm not sure how to respond to that."
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return "I'm having trouble connecting to my knowledge base."
            
    except Exception as e:
        print(f"Error in Hugging Face API: {e}")
        traceback.print_exc()
        return "I encountered an error while processing your request."

# Add this function for fallback responses

def get_fallback_response(query):
    """Generate a fallback response when API fails"""
    fallback_responses = [
        "I'm sorry, I don't have enough information to answer that properly.",
        "That's an interesting question. I'm still learning about that topic.",
        "I'm having trouble connecting to my knowledge base. Let me give a simple response.",
        "I understand you're asking about something, but I'm not quite sure how to answer yet."
    ]
    
    # Use different responses for different types of queries
    if "?" in query:
        return "That's an interesting question. I'll need to learn more about that topic."
    elif any(word in query.lower() for word in ["help", "assist", "support"]):
        return "I'm here to help. What specific assistance do you need?"
    elif any(word in query.lower() for word in ["thank", "thanks"]):
        return "You're welcome! Is there anything else I can help with?"
    else:
        import random
        return random.choice(fallback_responses)

# Update the process_command function to use Hugging Face
@eel.expose
def process_command(command):
    """Process user commands from the UI"""
    print(f"Received command: {command}")
    try:
        # Process built-in commands locally
        if "weather" in command.lower():
            response = "I'm sorry, I don't have access to weather information yet."
        elif "time" in command.lower():
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
        elif "hello" in command.lower() or "hi" in command.lower():
            response = "Hello! How can I help you today?"
        elif "date" in command.lower():
            from datetime import datetime
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}"
        elif "name" in command.lower():
            response = "My name is Jarvis. I'm your virtual assistant."
        else:
            # Use Hugging Face API for other queries
            try:
                print("Querying Hugging Face API...")
                response = get_huggingface_response(command)
                print(f"API response: {response}")
            except Exception as e:
                print(f"Error with Hugging Face API: {e}")
                response = get_fallback_response(command)
        
        # Log and speak the response
        print(f"Final response: {response}")
        speak_safely(response)
        
        return response
    except Exception as e:
        print(f"Error processing command: {e}")
        error_message = "I'm sorry, I encountered an error processing your command."
        speak_safely(error_message)
        traceback.print_exc()
        return error_message

@eel.expose
def listen_for_command():
    """Listen for voice command using microphone with better error handling"""
    recognizer = sr.Recognizer()
    
    try:
        print("Listening for voice command...")
        
        # Try to find a working microphone
        mic_found = False
        microphones = sr.Microphone.list_microphone_names()
        print(f"Available microphones: {microphones}")
        
        # Try default microphone first
        try:
            with sr.Microphone() as source:
                print("Using default microphone")
                recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = recognizer.listen(source, timeout=5)
                mic_found = True
        except Exception as e:
            print(f"Error with default microphone: {e}")
            
        # If default fails, try device index 0
        if not mic_found:
            try:
                print("Trying microphone with device_index=0")
                with sr.Microphone(device_index=0) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    mic_found = True
            except Exception as e:
                print(f"Error with device_index=0: {e}")
                
        # If we got audio, try to recognize it
        if mic_found:
            try:
                print("Got audio, recognizing...")
                text = recognizer.recognize_google(audio)
                print(f"Recognized: '{text}'")
                
                # Process the recognized command
                process_command(text)
                return text
            except sr.UnknownValueError:
                print("Could not understand audio")
                speak_safely("I couldn't understand what you said.")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results: {e}")
                speak_safely("I'm having trouble accessing the speech recognition service.")
                return ""
        else:
            error_msg = "No working microphone found"
            print(error_msg)
            speak_safely(error_msg)
            return ""
    except Exception as e:
        print(f"Error in voice recognition: {e}")
        traceback.print_exc()
        speak_safely("There was an error with the voice recognition system.")
        return ""

def simulate_hotword():
    """Simulate hotword detection"""
    while keep_running:
        time.sleep(30)  # Check every 30 seconds
        try:
            print("Simulating hotword activation")
            speak_safely("How can I help you?")
            
            # Optional: Also show a visual indicator in the UI
            eel.activateAssistant()  # Make sure to define this in your JS
        except Exception as e:
            print(f"Error in hotword simulation: {e}")

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
        # Start hotword simulation in background
        hotword_thread = threading.Thread(target=simulate_hotword, daemon=True)
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