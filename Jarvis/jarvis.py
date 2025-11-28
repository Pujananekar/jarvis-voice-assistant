# Jarvis/jarvis.py — Server-friendly (Option A)
import pyttsx3
import datetime
import wikipedia
import webbrowser as wb
import os
import random
import pyjokes
import time

# inside wishme()
speak("Welcome back, sir!")
print("Welcome back, sir!")
# add:
print("Deployed by Puja Nanekar — EC2 Demo")
speak("Deployed by Puja Nanekar — EC2 Demo")

engine = pyttsx3.init()
voices = engine.getProperty('voices')
# choose a default voice; index might vary per platform
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

COMMAND_FILE = os.path.expanduser("~/jarvis_command.txt")  # single-line command file

def speak(audio) -> None:
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        # TTS maybe unavailable on server; just print
        print("TTS error:", e)
        print("SPEAK:", audio)

def log(msg: str) -> None:
    print(f"[{datetime.datetime.now().isoformat()}] {msg}")

def time_cmd() -> None:
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is " + current_time)
    log("Time requested -> " + current_time)

def date_cmd() -> None:
    now = datetime.datetime.now()
    speak(f"The current date is {now.day} {now.strftime('%B')} {now.year}")
    log("Date requested -> " + f"{now.day}/{now.month}/{now.year}")

def wishme() -> None:
    # visible UI/text change for project
    log("Welcome back, sir!")
    log("Deployed by Puja Nanekar — EC2 Demo")
    speak("Welcome back. Deployed by Puja Nanekar. Jarvis at your service.")

def play_music(song_name=None) -> None:
    music_dir = os.path.expanduser("~/Music")
    if not os.path.exists(music_dir):
        speak("Music folder not found.")
        return
    songs = os.listdir(music_dir)
    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]
    if songs:
        song = random.choice(songs)
        song_path = os.path.join(music_dir, song)
        os.system(f'xdg-open "{song_path}" >/dev/null 2>&1 || true')
        speak(f"Playing {song}")
        log("Playing music: " + song)
    else:
        speak("No songs found.")
        log("No songs found in Music folder.")

def search_wikipedia(query):
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(query, sentences=2)
        speak(result)
        log("Wikipedia: " + result)
    except Exception as e:
        speak("I couldn't find anything on Wikipedia.")
        log("Wikipedia error: " + str(e))

def set_name(newname):
    try:
        with open(os.path.expanduser("~/assistant_name.txt"), "w") as f:
            f.write(newname)
        speak(f"Alright, I will be called {newname} from now on.")
        log("Assistant name set to: " + newname)
    except Exception as e:
        log("Error setting name: " + str(e))

def load_name():
    try:
        with open(os.path.expanduser("~/assistant_name.txt"), "r") as f:
            return f.read().strip()
    except:
        return "Jarvis"

def process_command_text(cmd: str) -> None:
    """cmd is a single-line lowercase string. Example:
       time
       date
       wikipedia who is alan turing
       play music happy
       set name jarvis2
       open youtube
       joke
       shutdown (won't actually shutdown server; will just log)
    """
    if not cmd:
        return
    cmd = cmd.strip()
    log("Processing command: " + cmd)
    if cmd == "time":
        time_cmd()
    elif cmd == "date":
        date_cmd()
    elif cmd.startswith("wikipedia"):
        query = cmd.replace("wikipedia", "", 1).strip()
        if query:
            search_wikipedia(query)
        else:
            speak("Please provide wiki query.")
    elif cmd.startswith("play music"):
        song = cmd.replace("play music", "", 1).strip()
        play_music(song if song else None)
    elif cmd.startswith("set name"):
        name = cmd.replace("set name", "", 1).strip()
        if name:
            set_name(name)
    elif cmd == "open youtube":
        wb.open("https://youtube.com")
        speak("Opening YouTube.")
    elif cmd == "joke" or "tell me a joke" in cmd:
        joke = pyjokes.get_joke()
        speak(joke)
        log("Joke told: " + joke)
    elif cmd == "status":
        speak("Jarvis is running.")
    elif cmd == "shutdown":
        speak("Shutdown command received. Not shutting down server for safety.")
        log("Shutdown requested but ignored on server.")
    else:
        speak("Unknown command: " + cmd)
        log("Unknown command: " + cmd)

def read_and_clear_command_file() -> str:
    try:
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                content = f.read().strip()
            # clear file after reading
            open(COMMAND_FILE, "w").close()
            return content
        return ""
    except Exception as e:
        log("Error reading command file: " + str(e))
        return ""

if __name__ == "__main__":
    wishme()
    assistant_name = load_name()
    log(f"{assistant_name} at your service. Waiting for commands (write single-line command to {COMMAND_FILE})")
    # make sure command file exists
    open(COMMAND_FILE, "a").close()

    while True:
        cmd = read_and_clear_command_file()
        if cmd:
            process_command_text(cmd.lower())
        # heartbeat log every 30 sec so Jenkins/console shows it's alive
        log("Heartbeat - waiting for commands...")
        time.sleep(30)
