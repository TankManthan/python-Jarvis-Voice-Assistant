import time
import pyttsx3
import requests
import wikipedia
import webbrowser
from datetime import datetime
import speech_recognition as sr
from countries import countries_list
from googleapiclient.discovery import build

 # Get from Google Cloud Console
API_KEY = "your api key here..." 
youtube = build("youtube", "v3", developerKey=API_KEY)

# Get from open weather api services
WEATHER_API="weather api key here..."

# For storing the notes
notes=[]

def speak(text):
    print(f"{text}")
    engine = pyttsx3.init()  # Re-initialize every time
    engine.say(text)
    engine.runAndWait()
    engine.stop()  # Ensure queue is cleared

def listen(timeout=5, phrase_time_limit=3):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = r.recognize_google(audio)
            print(f"Heard: {text}")
            return text
    except Exception as e:
        print("Listening error ! Say again...")
        return 

def play_song(query):
    if not query:
        speak("Please tell me the song name.")
        return
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        videoCategoryId="10",  # Music category
        maxResults=1
    )
    response = request.execute()
    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        webbrowser.open(url)
    else:
        print("No results found.")
        
def get_weather(city):
    global WEATHER_API
    # print(city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        weather_report = (
            f"The weather in {city} is {description}, "
            f"{temp}°C, feels like {feels_like}°C, humidity {humidity}%."
        )
        speak(weather_report)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")


def processCommand(command):
    if not command:
        return
    
    global notes
    cmd = command.lower()
    
    if "exit" in cmd:
        exit()
    elif "open youtube" in cmd:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open linkedin" in cmd:
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com")
    elif "open chrome" in cmd:
        speak("Opening Chrome website")
        webbrowser.open("https://www.google.com/chrome/")
    elif "open instagram" in cmd:
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com")
    elif "search" in cmd:
        query = cmd.replace("search", "").strip()
        speak(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif "time" in cmd:
        now = datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {now}")
    elif any(word in cmd for word in ["play music", "play song", "play video", "play", "music", "song", "video"]):
        song_name = cmd
        keywords = ["play music", "play song", "play video", "play", "music", "song", "video"]
        for keyword in keywords:
             if keyword in song_name:
                song_name = song_name.replace(keyword, "", 1).strip()
                break
        if song_name:
            play_song(song_name)
            speak(f"Playing {song_name}")
        else:
            speak("Which song do you want me to play?")
            song_name = listen(6,4)
            if song_name:
                play_song(song_name) 
                speak(f"Playing {song_name}")
    elif "weather" in cmd:
        country = ""
        for c in countries_list:
            if c.lower() in cmd:
                country = c
                break
        if not country:
            speak("No country found...")
        else:
            get_weather(country)

    elif "take note" in cmd or "take a note" in cmd:
        speak("What should I write?")
        note = listen(10,6)
        if note:
            notes.append(f"{note} . Noting timing was {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            speak("Noted.")
        else:
            speak("I didn't catch the note.")
    elif "my note" in cmd or "my notes" in cmd:
        if notes:
            for n in notes:
                speak(n)
        else:
            speak("You don't have any notes yet.")
    elif ("wikipedia" in cmd) or ("information of" in cmd) or ("who is" in cmd):
        query = cmd.replace("search wikipedia for", "")
        try:
            result = wikipedia.summary(query, sentences=3)
            speak(result)
        except Exception as e:
            speak("No information found .")
    else:
        print("Sorry, I don't know that command.")

if __name__ == "__main__":
    speak("Initializing Jarvis...")
    speak("Say 'Jarvis' to activate me.")
    active = False 
     
    while True:
        if not active:  
            # Waiting for wake word
            trigger_word = listen(2,2)
            if trigger_word:
                wake = trigger_word.lower()
                if "jarvis" in wake:
                    active = True
                    speak("Yaa, tell me?")
                elif wake in ["exit", "stop the code"]:
                    speak("See you soon, BYE...")
                    break
                else:
                    print("Listening for 'Jarvis'...")
            else:
                print("")
        
        else:
            # Active mode: keep listening for commands
            command = listen()

            if not command:
                print("I didn’t catch that. Listening...")
                continue

            cmd = command.lower()

            if "jarvis" in cmd:
                speak("Yes, I am here...")

            elif cmd in ["exit", "stop the code"]:
                speak("See you soon, BYE...")
                active = False  # deactivate
                break

            else:
                processCommand(command)