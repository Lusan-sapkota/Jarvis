import os
import eel
from backend.auth import recoganize
from backend.auth.recoganize import AuthenticateFace
from backend.feature import *
from backend.command import *
import sys



def start():
    
    eel.init("frontend") 
    
    play_assistant_sound()
    @eel.expose
    def init():
        eel.hideLoader()
        flag = recoganize.AuthenticateFace()
        if flag ==1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
        
    def open_browser():
        url = "http://127.0.0.1:8000/index.html"

        if sys.platform == "win32":
            os.system(f'start msedge.exe --app="{url}"')  # Windows (Edge as PWA)
        elif sys.platform == "darwin":
            os.system(f'open "{url}"')  # macOS (opens in default browser)
        else:
            os.system(f'xdg-open "{url}"')  # Linux (opens in default browser)
        
    open_browser()
    
    eel.start("index.html", mode=None, host="localhost", block=True) 

