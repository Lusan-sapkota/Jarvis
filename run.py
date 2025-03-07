import multiprocessing
import signal
import sys

def startJarvis():
    print("Process 1 Starting...")
    from main import start
    start()
    
def listenHotword():
    print("Process 2 Starting...")
    from backend.feature import hotword
    hotword()

def handle_interrupt(sig, frame):
    print("\nInterrupted by user. Shutting down...")
    for p in [process1, process2]:
        if p.is_alive():
            p.terminate()
            p.join()
    print("System is terminated.")
    sys.exit(0)
    
if __name__ == "__main__":
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_interrupt)
    
    process1 = multiprocessing.Process(target=startJarvis)
    process2 = multiprocessing.Process(target=listenHotword)
    
    process1.start()
    process2.start()
    
    # Wait for both processes
    try:
        process1.join()
        process2.join()
    except KeyboardInterrupt:
        pass
        
    print("System is terminated.")