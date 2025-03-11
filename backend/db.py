import csv
import sqlite3

conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

def initialize_linux_commands():
    """Initialize the database with common Linux applications"""
    try:
        # Check if we already have entries
        cursor.execute("SELECT COUNT(*) FROM sys_command")
        count = cursor.fetchone()[0]
        
        # Only add if we have fewer than 5 entries
        if count < 5:
            linux_apps = [
                ("chrome", "google-chrome"),
                ("firefox", "firefox"),
                ("code", "code"),
                ("terminal", "gnome-terminal"),
                ("files", "nautilus"),
                ("calculator", "gnome-calculator"),
                ("text editor", "gedit"),
                ("spotify", "spotify"),
                ("discord", "discord"),
                ("vlc", "vlc"),
                ("obs", "obs-studio"),
                ("android studio", "/opt/android-studio/bin/studio.sh")
            ]
            
            for name, path in linux_apps:
                try:
                    cursor.execute("INSERT INTO sys_command VALUES (null, ?, ?)", (name, path))
                except:
                    # Skip if already exists
                    pass
            
            conn.commit()
            print("Linux applications added to database")
    except Exception as e:
        print(f"Error initializing Linux commands: {e}")

# Call the function when the module is imported
initialize_linux_commands()
