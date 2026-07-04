import speech_recognition as sr
import webbrowser
import musiclibrary 
import requests
import google.generativeai as genai
from gtts import gTTS
import pygame
import os
import time
import datetime
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

recognizer = sr.Recognizer()
recognizer.energy_threshold = 250
recognizer.pause_threshold = 0.6

mic = sr.Microphone()

with mic as source:

    recognizer.adjust_for_ambient_noise(source, duration=0.3)

def speak(text, show_text=True):
    try:
        filename = "temp.mp3"
        gTTS(text=text, lang='en').save(filename)

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        if show_text:
            print("JARVIS:", text)

        while pygame.mixer.music.get_busy():
            time.sleep(0.05)

        pygame.mixer.quit()
        os.remove(filename)

    except Exception as e:
        print("Voice Error:", e)


def detect_category(text):
    text = text.lower()

    if "sport" in text or "cricket" in text:
        return "sports"
    elif "business" in text:
        return "business"
    elif "tech" in text:
        return "technology"
    elif "health" in text:
        return "health"
    elif "politics" in text:
        return "politics"
    else:
        return "general"


# FINAL CLEAN NEWS FUNCTION
def fetch_news(category):
    news = []

    countries = {
        "in": "India",
        "us": "United States",
        "gb": "United Kingdom",
        "au": "Australia",
        "ca": "Canada",
        "de": "Germany"
    }

    seen_titles = set()

    for code, name in countries.items():
        try:
            url = (
                f"https://gnews.io/api/v4/top-headlines?"
                f"country={code}&category={category}"
                f"&lang=en&max=10&apikey={NEWS_API_KEY}"
            )

            data = requests.get(url, timeout=8).json()

            if "articles" not in data:
                continue

            for article in data["articles"]:

                title = article.get("title")

                if not title:
                    continue

                if title in seen_titles:
                    continue

                seen_titles.add(title)

                news.append({
                    "title": title,
                    "country": name,
                    "date": article.get("publishedAt", "")[:10]
                })

        except Exception as e:
            print(f"{name} :", e)

    latest_news = news[:3]

    past_news = news[3:6]

    return latest_news, past_news


def processCommand(c):
    c = c.lower().strip()
    print("COMMAND RECEIVED:", c)

    if any(x in c for x in ["who are you", "who are u", "who're you"]):
       speak("I am Jarvis, your personal AI assistant.")

    elif any(x in c for x in ["how are you", "how r you"]):
      speak("I am doing great! Thank you.")

    elif "open google" in c:
        speak("Opening Google")
        webbrowser.open("https://google.com")

    elif "open youtube" in c:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")

    elif "open instagram" in c:
        speak("Opening Instagram")
        webbrowser.open("https://instagram.com")

    elif "open facebook" in c:
        speak("Opening Facebook")
        webbrowser.open("https://facebook.com")

    elif "open linkedin" in c:
        speak("Opening LinkedIn")
        webbrowser.open("https://linkedin.com")

    elif "open whatsapp" in c:
        speak("Opening whatsapp")
        webbrowser.open("https://whatsapp.com")


    elif "news" in c:
        try:
            print("\nChoose category:")
            print("sports | business | technology | health | politics | general")

            speak("Sure! Tell me the category")

            with mic as source:
                audio = recognizer.listen(source, timeout=4, phrase_time_limit=4)

            try:
                category_input = recognizer.recognize_google(audio)
            except:
                category_input = "general"

            category = detect_category(category_input)

            print("Selected category:", category)
            speak(f"Category selected {category}")
            speak("Fetching news")

            latest, past = fetch_news(category)

            print("\n--- LATEST NEWS ---")
            speak("Latest news")

            for n in latest:
                line = f"{n['title']} ({n['country']} - {n['date']})"
                print(line)
                speak(line, show_text=False)

            print("\n--- PAST NEWS ---")
            speak("Past news")

            for n in past:
                line = f"{n['title']} ({n['country']} - {n['date']})"
                print(line)
                speak(line, show_text=False)

        except Exception as e:
            print("NEWS ERROR:", e)
            speak("News not available")


    elif "play" in c:
        song_query = c.replace("play", "").strip().lower()

        found = False

        for key in musiclibrary.music:
            if key in song_query or song_query in key:
                speak(f"Playing {key}")
                webbrowser.open(musiclibrary.music[key])
                found = True
                break

        if not found:
            speak("Song not found")


    else:
        try:
            speak("Let me think")
            response = model.generate_content(c)

            if response and response.text:
                speak(response.text)
            else:
                speak("I could not answer")

        except:
            speak("AI not responding")


if __name__ == "__main__":
    speak("Initializing jarvis")

    while True:
        try:
            print("Listening for jarvis...")

            with mic as source:
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=4)

            word = recognizer.recognize_google(audio).lower()

            if "jarvis" in word:
                speak("yes")

                with mic as source:
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=5)

                command = recognizer.recognize_google(audio)
                processCommand(command)

        except sr.WaitTimeoutError:
            continue

        except Exception as e:
            print("Error:", e)