# VAM — Voice Assistant Module
### Computer Assistant Using Python
**By Muhammad Anas Khokhar | 2019-ag-9732**
University of Agriculture Faisalabad Sub Campus, Toba Tek Singh

---

## Features

| Feature | Command Example |
|---|---|
| Open Google | "open google" |
| Open YouTube | "open youtube" |
| Wikipedia Search | "what is artificial intelligence" |
| Weather | "weather in Lahore" |
| Tell a Joke | "tell me a joke" |
| Open Notepad | "open notepad" |
| Open Calculator | "open calculator" |
| Open CMD | "open command prompt" |
| Open VS Code | "open vs code" |
| Current Time | "what time is it" |
| Today's Date | "what date is today" |
| Play Music | "play Imagine Dragons on youtube" |
| Google Search | "search for Python tutorial" |
| Read PDF | Use the PDF upload zone |
| Set Reminder | "remind me to drink water" |
| System Info | "system info" |
| IP Address | "my ip address" |
| About VAM | "who are you" |

---

## Setup Instructions

### Step 1 — Install Python
Make sure Python 3.8 or newer is installed.
Download from: https://www.python.org/downloads/

### Step 2 — Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

If you're on Windows and pyttsx3 gives issues:
```bash
pip install pywin32
```

For microphone support on Linux:
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install pyaudio
```

### Step 4 — Run VAM
```bash
python app.py
```

### Step 5 — Open Browser
Go to: **http://127.0.0.1:5000**

---

## Tech Stack

- **Python 3** — Core language
- **Flask** — Web server & backend
- **pyttsx3** — Text-to-speech (offline)
- **SpeechRecognition** — Voice input via microphone
- **wikipedia** — Wikipedia search
- **pyjokes** — Jokes library
- **PyPDF2** — PDF reading
- **requests** — Weather via wttr.in
- **webbrowser** — Open websites
- **subprocess** — Open applications

---

## Libraries Used (from Report)

| Library | Purpose |
|---|---|
| pyttsx3 | Text to Speech (offline) |
| SpeechRecognition | Voice to Text |
| wikipedia | Wikipedia Searches |
| pywhatkit | WhatsApp & YouTube |
| pyjokes | Jokes |
| PyPDF2 | Read/parse PDFs |
| smtplib | Email sending |
| requests | HTTP requests & weather |
| webbrowser | Open websites |
| os / subprocess | System & app control |

---

## Project Structure
```
VAM/
├── app.py              ← Main Flask backend (all logic)
├── requirements.txt    ← All dependencies
├── README.md           ← This file
└── templates/
    └── index.html      ← 3D modern frontend
```

---

## Troubleshooting

**Voice not working?**
→ Install PyAudio: `pip install pyaudio`
→ Check microphone permissions in your OS settings

**pyttsx3 error on Windows?**
→ Run: `pip install pywin32`

**Wikipedia not working?**
→ Check internet connection
→ Run: `pip install wikipedia --upgrade`

**Port already in use?**
→ Change port in app.py: `app.run(port=5001)`
