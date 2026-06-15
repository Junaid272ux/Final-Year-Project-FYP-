"""
VAM - Voice Assistant Module
Computer Assistant Using Python
Author: Muhammad Junaid Ali (2022-ag-6336)
"""

import os
import sys
import json
import datetime
import webbrowser
import subprocess
import threading
import random
import time
import socket
from flask import Flask, render_template, request, jsonify

# ─── Optional imports with graceful fallback ──────────────────────────────────

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import wikipedia
    WIKI_AVAILABLE = True
except ImportError:
    WIKI_AVAILABLE = False

try:
    import pyjokes
    JOKES_AVAILABLE = True
except ImportError:
    JOKES_AVAILABLE = False

try:
    import requests as req_lib
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False  

try:
    from groq import Groq
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import smtplib
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False

try:
    import pywhatkit as kit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# ─── Groq AI Client (Free) ────────────────────────────────────────────────────
GROQ_API_KEY = "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"   # ← paste your key here
ai_client = None

def init_ai():
    global ai_client
    if not AI_AVAILABLE:
        print("[AI] Groq not installed. Run: pip install groq")
        return
    try:
        ai_client = Groq(api_key=GROQ_API_KEY)
        print("[AI] Groq AI ready — free unlimited answers enabled.")
    except Exception as e:
        print(f"[AI] Groq init failed: {e}")

def ask_ai(question):
    """Ask Groq AI any question and get a spoken-friendly answer."""
    if not ai_client:
        return None
    try:
        chat = ai_client.chat.completions.create(
            model="llama3-8b-8192",   # free model on Groq
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are VAM, a smart voice assistant on a desktop computer. "
                        "Answer every question in 2 to 3 short clear sentences. "
                        "Never use bullet points, markdown, asterisks, or headers. "
                        "Speak like a human assistant would."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI] Groq error: {e}")
        return None

# ─── Flask App ────────────────────────────────────────────────────────────────

app = Flask(__name__)

# ─── TTS Engine ───────────────────────────────────────────────────────────────

# ─── TTS Engine ───────────────────────────────────────────────────────────────
# FIX: pyttsx3 cannot safely share one engine across threads.
# Solution: create a FRESH engine inside each speak() call.
# This guarantees every response is spoken, not just the first one.

tts_lock = threading.Lock()   # ensures only one voice plays at a time


def init_tts():
    """Verify pyttsx3 works at startup. No persistent engine stored."""
    if not TTS_AVAILABLE:
        print("[TTS] pyttsx3 not installed — voice output disabled.")
        return
    try:
        test_engine = pyttsx3.init()
        voices = test_engine.getProperty("voices")
        count = len(voices) if voices else 0
        test_engine.stop()
        del test_engine
        print(f"[TTS] pyttsx3 ready — {count} voice(s) available.")
    except Exception as e:
        print(f"[TTS] Init check failed: {e}")


def speak(text):
    """
    Speak text by creating a FRESH pyttsx3 engine on every call.
    This fixes the one-time-speak bug caused by shared engine
    state corruption after the first runAndWait() call.
    """
    if not TTS_AVAILABLE:
        return
    if not text or not text.strip():
        return

    def _speak():
        with tts_lock:
            engine = None
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty("voices")
                if voices:
                    engine.setProperty("voice", voices[0].id)
                engine.setProperty("rate", 170)
                engine.setProperty("volume", 1.0)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[TTS] Speak error: {e}")
            finally:
                if engine:
                    try:
                        engine.stop()
                    except Exception:
                        pass
                    try:
                        del engine
                    except Exception:
                        pass

    threading.Thread(target=_speak, daemon=True).start()


# ─── Time-based greeting ──────────────────────────────────────────────────────

def get_greeting():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"


def get_time():
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")


def get_date():
    now = datetime.datetime.now()
    return now.strftime("%A, %B %d, %Y")


# ─── Core command processor ───────────────────────────────────────────────────

def process_command(query: str) -> dict:
    """
    Takes a text command (from voice or typed) and returns a response dict:
    { "response": str, "action": str, "data": any, "success": bool }
    """
    query = query.strip().lower()
    result = {"response": "", "action": "none", "data": None, "success": True}

    # ── Greeting / Wake ──────────────────────────────────────────────────────
    if any(w in query for w in ["hello", "hi vam", "hey vam", "hi there"]):
        greet = get_greeting()
        result["response"] = f"{greet}! I'm VAM, your personal computer assistant. How can I help you?"
        result["action"] = "greet"

    elif any(w in query for w in ["good morning", "good afternoon", "good evening"]):
        result["response"] = f"{get_greeting()} to you too! Ready to assist."
        result["action"] = "greet"

    elif "wake up" in query:
        result["response"] = f"{get_greeting()}! VAM is awake and ready. What can I do for you?"
        result["action"] = "wake"

    # ── Time & Date ──────────────────────────────────────────────────────────
    elif any(w in query for w in ["what time", "current time", "tell me the time", "time now"]):
        t = get_time()
        result["response"] = f"The current time is {t}."
        result["action"] = "time"
        result["data"] = t

    elif any(w in query for w in ["what date", "today's date", "current date", "what day"]):
        d = get_date()
        result["response"] = f"Today is {d}."
        result["action"] = "date"
        result["data"] = d

    # ── Open Websites ────────────────────────────────────────────────────────
    elif "open google" in query or "search google" in query:
        webbrowser.open("https://www.google.com")
        result["response"] = "Opening Google for you right now!"
        result["action"] = "open_website"
        result["data"] = "https://www.google.com"

    elif "open youtube" in query:
        webbrowser.open("https://www.youtube.com")
        result["response"] = "Opening YouTube! Enjoy your videos."
        result["action"] = "open_website"
        result["data"] = "https://www.youtube.com"

    elif "open facebook" in query:
        webbrowser.open("https://www.facebook.com")
        result["response"] = "Opening Facebook!"
        result["action"] = "open_website"
        result["data"] = "https://www.facebook.com"

    elif "open twitter" in query or "open x" in query:
        webbrowser.open("https://www.twitter.com")
        result["response"] = "Opening Twitter / X!"
        result["action"] = "open_website"
        result["data"] = "https://www.twitter.com"

    elif "open instagram" in query:
        webbrowser.open("https://www.instagram.com")
        result["response"] = "Opening Instagram!"
        result["action"] = "open_website"
        result["data"] = "https://www.instagram.com"

    elif "open github" in query:
        webbrowser.open("https://www.github.com")
        result["response"] = "Opening GitHub!"
        result["action"] = "open_website"
        result["data"] = "https://www.github.com"

    elif "open gmail" in query:
        webbrowser.open("https://mail.google.com")
        result["response"] = "Opening Gmail!"
        result["action"] = "open_website"
        result["data"] = "https://mail.google.com"

    elif "open chatgpt" in query:
        webbrowser.open("https://chat.openai.com")
        result["response"] = "Opening ChatGPT!"
        result["action"] = "open_website"
        result["data"] = "https://chat.openai.com"

    # ── Google Search ────────────────────────────────────────────────────────
    elif "search for" in query or "google" in query:
        search_term = query.replace("search for", "").replace("google", "").strip()
        if search_term:
            url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            webbrowser.open(url)
            result["response"] = f"Searching Google for: {search_term}"
            result["action"] = "search"
            result["data"] = url
        else:
            webbrowser.open("https://www.google.com")
            result["response"] = "Opening Google for you!"
            result["action"] = "open_website"

    # ── YouTube Search / Play ────────────────────────────────────────────────
    elif "play" in query and ("youtube" in query or "music" in query or "song" in query or "video" in query):
        search_term = query
        for rm in ["play", "on youtube", "youtube", "music", "song", "video"]:
            search_term = search_term.replace(rm, "").strip()
        if search_term:
            url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            webbrowser.open(url)
            result["response"] = f"Searching YouTube for: {search_term}. Enjoy!"
            result["action"] = "play_music"
            result["data"] = url
        else:
            webbrowser.open("https://www.youtube.com")
            result["response"] = "Opening YouTube!"
            result["action"] = "open_website"

    elif "play music" in query or "play song" in query:
        webbrowser.open("https://www.youtube.com")
        result["response"] = "Opening YouTube for music!"
        result["action"] = "play_music"

    # ── Wikipedia ────────────────────────────────────────────────────────────
    elif "wikipedia" in query or "who is" in query or "what is" in query:
        search_term = (query.replace("wikipedia", "")
                           .replace("who is", "")
                           .replace("what is", "")
                           .strip())
        if not search_term:
            result["response"] = "Please tell me what you want to search on Wikipedia."
            result["action"] = "wikipedia_empty"
        elif WIKI_AVAILABLE:
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(search_term, sentences=3)
                result["response"] = f"According to Wikipedia: {summary}"
                result["action"] = "wikipedia"
                result["data"] = summary
            except wikipedia.exceptions.DisambiguationError as e:
                result["response"] = f"Multiple results found. Did you mean: {', '.join(e.options[:4])}?"
                result["action"] = "wikipedia_disambiguation"
            except wikipedia.exceptions.PageError:
                result["response"] = f"Sorry, I couldn't find anything about '{search_term}' on Wikipedia."
                result["action"] = "wikipedia_not_found"
            except Exception as e:
                url = f"https://en.wikipedia.org/wiki/{search_term.replace(' ', '_')}"
                webbrowser.open(url)
                result["response"] = f"Opening Wikipedia page for {search_term}."
                result["action"] = "wikipedia_browser"
        else:
            url = f"https://en.wikipedia.org/wiki/{search_term.replace(' ', '_')}"
            webbrowser.open(url)
            result["response"] = f"Opening Wikipedia for {search_term}."
            result["action"] = "wikipedia_browser"

    # ── Weather ──────────────────────────────────────────────────────────────
    elif "weather" in query:
        city = query.replace("weather", "").replace("in", "").replace("of", "").strip()
        if not city:
            city = "Faisalabad"
        if REQUESTS_AVAILABLE:
            try:
                api_key = "demo"
                url = f"https://wttr.in/{city.replace(' ', '+')}?format=3"
                resp = req_lib.get(url, timeout=5)
                if resp.status_code == 200:
                    result["response"] = f"Weather update: {resp.text.strip()}"
                    result["action"] = "weather"
                    result["data"] = resp.text.strip()
                else:
                    webbrowser.open(f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}")
                    result["response"] = f"Opening weather search for {city}."
                    result["action"] = "weather_browser"
            except Exception:
                webbrowser.open(f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}")
                result["response"] = f"Searching weather for {city} on Google."
                result["action"] = "weather_browser"
        else:
            webbrowser.open(f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}")
            result["response"] = f"Searching weather for {city}."
            result["action"] = "weather_browser"

    # ── Jokes ────────────────────────────────────────────────────────────────
    elif any(w in query for w in ["joke", "funny", "make me laugh", "tell me a joke"]):
        if JOKES_AVAILABLE:
            joke = pyjokes.get_joke()
            result["response"] = joke
        else:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "Why did the developer go broke? Because he used up all his cache!",
                "A SQL query walks into a bar, walks up to two tables and asks... Can I join you?",
                "Why do Java developers wear glasses? Because they don't C#!",
                "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
                "Why was the JavaScript developer sad? Because he didn't know how to 'null' his feelings.",
                "There are 10 types of people: those who understand binary and those who don't.",
            ]
            result["response"] = random.choice(jokes)
        result["action"] = "joke"

    # ── Open Applications ────────────────────────────────────────────────────
    elif "open notepad" in query:
        try:
            os.system("start notepad.exe")
            result["response"] = "Opening Notepad for you!"
        except Exception:
            result["response"] = "Sorry, I could not open Notepad."
        result["action"] = "open_app"

    elif "open calculator" in query:
        try:
            os.system("start calc.exe")
            result["response"] = "Opening Calculator!"
        except Exception:
            result["response"] = "Sorry, I could not open Calculator."
        result["action"] = "open_app"

    elif "open command prompt" in query or "open cmd" in query or "open terminal" in query:
        try:
            subprocess.Popen(["cmd.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            result["response"] = "Opening Command Prompt!"
        except Exception:
            try:
                subprocess.Popen(["start", "cmd"], shell=True)
                result["response"] = "Opening Command Prompt!"
            except Exception:
                try:
                    os.system("start cmd")
                    result["response"] = "Opening Command Prompt!"
                except Exception:
                    result["response"] = "Sorry, I could not open the terminal."
        result["action"] = "open_app"

    elif "open file manager" in query or "open explorer" in query:
        try:
            subprocess.Popen(["explorer.exe"])
            result["response"] = "Opening File Explorer!"
        except FileNotFoundError:
            try:
                subprocess.Popen(["nautilus"])
                result["response"] = "Opening File Manager!"
            except FileNotFoundError:
                result["response"] = "Sorry, I couldn't open the file manager."
        result["action"] = "open_app"

    elif "open vs code" in query or "open vscode" in query or "open visual studio" in query:
        opened = False

        # Method 1 — try code command directly
        try:
            subprocess.Popen(["code"], shell=True)
            result["response"] = "Opening VS Code!"
            opened = True
        except Exception:
            pass

        # Method 2 — try common Windows install paths
        if not opened:
            vs_paths = [
                r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.environ.get("USERNAME", "")),
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            ]
            for path in vs_paths:
                if os.path.exists(path):
                    try:
                        subprocess.Popen([path])
                        result["response"] = "Opening VS Code!"
                        opened = True
                        break
                    except Exception:
                        pass

        # Method 3 — use shell start command
        if not opened:
            try:
                os.system("start code")
                result["response"] = "Opening VS Code!"
                opened = True
            except Exception:
                pass

        if not opened:
            result["response"] = "VS Code not found. Please install it from https://code.visualstudio.com"

        result["action"] = "open_app"
    # ── Conversations ────────────────────────────────────────────────────────
    elif "how are you" in query:
        result["response"] = "I'm doing perfectly, thank you for asking! Ready to assist you with anything."
        result["action"] = "conversation"

    elif "i am fine" in query or "i'm fine" in query or "i'm good" in query:
        result["response"] = "That's great to hear! How can I help you today?"
        result["action"] = "conversation"

    elif "thank you" in query or "thanks" in query:
        result["response"] = "You're most welcome! I'm always here for you."
        result["action"] = "conversation"

    elif "who are you" in query or "what are you" in query:
        result["response"] = ("I'm VAM — Voice Assistant Module, your personal computer assistant "
                              "built with Python by Muhammad Junaid Ali . I can open websites, "
                              "search Wikipedia, tell jokes, check weather, and much more!")
        result["action"] = "conversation"

    elif "who made you" in query or "who created you" in query or "who built you" in query:
        result["response"] = ("I was created by Muhammad Junaid Ali as a Final Year Project "
                              "at the University of Agriculture Faisalabad Sub Campus, Toba Tek Singh.")
        result["action"] = "conversation"

    elif any(w in query for w in ["what can you do", "your features", "help me", "capabilities"]):
        result["response"] = ("I can do many things for you! Open websites like Google, YouTube, and Wikipedia. "
                              "Search the web, check weather, tell jokes, open applications like Notepad, "
                              "Calculator, and CMD. I can also read PDFs, and have basic conversations. "
                              "Just ask me anything!")
        result["action"] = "capabilities"

    elif "good night" in query:
        result["response"] = "Good night! Sweet dreams. I'll be here whenever you need me."
        result["action"] = "conversation"

    elif "bye" in query or "goodbye" in query or "go to sleep" in query or "sleep" in query:
        result["response"] = "Goodbye! You can call me anytime. Take care!"
        result["action"] = "sleep"

    # ── System Info ──────────────────────────────────────────────────────────
    elif "system info" in query or "computer info" in query or "os info" in query:
        import platform
        info = (f"OS: {platform.system()} {platform.release()} | "
                f"Machine: {platform.machine()} | "
                f"Python: {platform.python_version()}")
        result["response"] = f"System info: {info}"
        result["action"] = "system_info"
        result["data"] = info

    elif "ip address" in query or "my ip" in query:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            result["response"] = f"Your local IP address is {ip} and hostname is {hostname}."
            result["action"] = "ip_address"
            result["data"] = ip
        except Exception:
            result["response"] = "Sorry, I couldn't retrieve your IP address."
            result["action"] = "ip_error"

    # ── Read PDF ─────────────────────────────────────────────────────────────
    elif "read pdf" in query or "open pdf" in query:
        result["response"] = ("To read a PDF, please use the PDF Reader section on the left panel. "
                              "You can upload your PDF file there and I'll read it for you.")
        result["action"] = "read_pdf"

    # ── Reminders ────────────────────────────────────────────────────────────
    elif "remind me" in query or "set reminder" in query:
        reminder_text = (query.replace("remind me to", "")
                              .replace("remind me", "")
                              .replace("set reminder", "")
                              .strip())
        if reminder_text:
            result["response"] = (f"Got it! I've noted your reminder: '{reminder_text}'. "
                                  f"I'll remind you about this.")
            result["action"] = "reminder"
            result["data"] = reminder_text
        else:
            result["response"] = "What would you like me to remind you about?"
            result["action"] = "reminder_empty"

    # ── WhatsApp (pywhatkit) ─────────────────────────────────────────────────
    elif "whatsapp" in query or "send whatsapp" in query or "send message" in query:
        if PYWHATKIT_AVAILABLE:
            result["response"] = ("To send a WhatsApp message, use the format: "
                                  "'send whatsapp to [number] message [your message]'. "
                                  "pywhatkit is ready and installed.")
        else:
            result["response"] = ("pywhatkit is not installed. Run: pip install pywhatkit. "
                                  "Once installed, VAM can send WhatsApp messages for you.")
        result["action"] = "whatsapp"

    # ── Screenshot (pyautogui) ────────────────────────────────────────────────
    elif "take screenshot" in query or "screenshot" in query or "capture screen" in query:
        if PYAUTOGUI_AVAILABLE:
            try:
                import os as _os
                screenshot_path = _os.path.join(_os.path.expanduser("~"), "Desktop", "vam_screenshot.png")
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                result["response"] = f"Screenshot saved to your Desktop as 'vam_screenshot.png'!"
                result["action"] = "screenshot"
                result["data"] = screenshot_path
            except Exception as e:
                result["response"] = f"Screenshot failed: {str(e)}"
                result["action"] = "screenshot_error"
        else:
            result["response"] = "pyautogui is not installed. Run: pip install pyautogui to enable screenshots."
            result["action"] = "screenshot_missing"

    # ── Music ────────────────────────────────────────────────────────────────
    elif "play music" in query or "music" in query:
        webbrowser.open("https://www.youtube.com/results?search_query=best+music+playlist")
        result["response"] = "Playing music on YouTube! Sit back and enjoy."
        result["action"] = "play_music"

    # ── Calculator ───────────────────────────────────────────────────────────
    elif "calculate" in query or "what is" in query and any(op in query for op in ["+", "-", "*", "/"]):
        expr = (query.replace("calculate", "")
                     .replace("what is", "")
                     .strip())
        try:
            # Only allow safe math expressions
            allowed = set("0123456789+-*/()., ")
            if all(c in allowed for c in expr):
                answer = eval(expr)
                result["response"] = f"The answer is: {answer}"
                result["action"] = "calculate"
                result["data"] = answer
            else:
                result["response"] = "Sorry, I can only calculate basic math expressions."
                result["action"] = "calculate_error"
        except Exception:
            result["response"] = "Sorry, I couldn't calculate that. Please try again."
            result["action"] = "calculate_error"

    # ── AI Fallback — answers EVERYTHING ─────────────────────────────────────
    else:
        ai_answer = ask_ai(query) if ai_client else None

        if ai_answer:
            result["response"] = ai_answer
            result["action"] = "ai_answer"
        else:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            result["response"] = f"Let me search that for you: {query}"
            result["action"] = "fallback_search"
            result["data"] = search_url

    # Speak the response
    speak(result["response"])
    return result


# ─── Flask Routes ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    greeting = get_greeting()
    current_time = get_time()
    current_date = get_date()
    return render_template("index.html",
                           greeting=greeting,
                           current_time=current_time,
                           current_date=current_date,
                           tts_available=TTS_AVAILABLE,
                           sr_available=SR_AVAILABLE)


@app.route("/command", methods=["POST"])
def command():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"response": "Please say or type something.", "action": "empty", "success": False})
    result = process_command(query)
    return jsonify(result)


@app.route("/listen", methods=["POST"])
def listen():
    """Activate microphone and return recognized speech."""
    if not SR_AVAILABLE:
        return jsonify({"success": False, "text": "",
                        "error": "SpeechRecognition library not installed. Install with: pip install SpeechRecognition"})
    try:
        r = sr.Recognizer()
        r.pause_threshold = 1
        r.energy_threshold = 300
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        text = r.recognize_google(audio, language='en-in')
        return jsonify({"success": True, "text": text})
    except sr.WaitTimeoutError:
        return jsonify({"success": False, "text": "", "error": "No speech detected. Please try again."})
    except sr.UnknownValueError:
        return jsonify({"success": False, "text": "", "error": "Couldn't understand. Please speak clearly."})
    except sr.RequestError as e:
        return jsonify({"success": False, "text": "", "error": f"Speech service error: {str(e)}"})
    except OSError:
        return jsonify({"success": False, "text": "", "error": "No microphone found. Please check your microphone."})
    except Exception as e:
        return jsonify({"success": False, "text": "", "error": f"Error: {str(e)}"})


@app.route("/read_pdf", methods=["POST"])
def read_pdf():
    """Read text from uploaded PDF."""
    if "pdf" not in request.files:
        return jsonify({"success": False, "text": "", "error": "No PDF file uploaded."})
    pdf_file = request.files["pdf"]
    if not PDF_AVAILABLE:
        return jsonify({"success": False, "text": "", "error": "PyPDF2 not installed. Run: pip install PyPDF2"})
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for i, page in enumerate(reader.pages):
            text += f"\n--- Page {i+1} ---\n"
            text += page.extract_text() or ""
        if not text.strip():
            return jsonify({"success": False, "text": "", "error": "No readable text found in PDF."})
        speak(f"I found {len(reader.pages)} pages in your PDF. Here is the content.")
        return jsonify({"success": True, "text": text, "pages": len(reader.pages)})
    except Exception as e:
        return jsonify({"success": False, "text": "", "error": f"PDF read error: {str(e)}"})


@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "tts": TTS_AVAILABLE,
        "speech_recognition": SR_AVAILABLE,
        "wikipedia": WIKI_AVAILABLE,
        "jokes": JOKES_AVAILABLE,
        "requests": REQUESTS_AVAILABLE,
        "pdf": PDF_AVAILABLE,
        "smtp": SMTP_AVAILABLE,
        "pywhatkit": PYWHATKIT_AVAILABLE,
        "pyautogui": PYAUTOGUI_AVAILABLE,
        "time": get_time(),
        "date": get_date(),
        "greeting": get_greeting()
    })


# ─── Start ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  VAM - Voice Assistant Module")
    print("  Computer Assistant Using Python")
    print("  By Muhammad Junaid Ali (2022-ag-6336)")
    # print("  UAF Sub Campus, Toba Tek Singh")
    print("=" * 60)
    print(f"\n  Starting server at: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop.\n")
    init_tts()
    init_ai()
    app.run(debug=False, host="127.0.0.1", port=5000, threaded=True)
