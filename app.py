import sqlite3
import os
import datetime
from gtts import gTTS
from difflib import SequenceMatcher

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect("nexvoice.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS profile (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

conn.commit()

# =========================
# SETTINGS
# =========================
settings = {
    "voice": True
}

knowledge = {
    "nexvora": "Nexvora একটি AI studio platform",
    "ai": "AI মানে Artificial Intelligence",
    "gpt": "GPT একটি language model"
}

chat_history = []

# =========================
# VOICE SYSTEM
# =========================
def speak(text):
    if not settings["voice"]:
        return
    try:
        tts = gTTS(text=text, lang='bn')
        tts.save("voice.mp3")
        os.system("mpv voice.mp3 --quiet")
    except:
        print("Voice error")

# =========================
# SIMILARITY
# =========================
def sim(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# =========================
# MEMORY SYSTEM (RAG)
# =========================
def save_memory(q, a):
    cursor.execute("INSERT INTO memory (question, answer) VALUES (?, ?)", (q, a))
    conn.commit()

def smart_search(text):
    cursor.execute("SELECT question, answer FROM memory")
    rows = cursor.fetchall()

    best_score = 0
    best_answer = None

    for q, a in rows:
        score = sim(text, q)

        if text in q or q in text:
            return a

        if score > best_score:
            best_score = score
            best_answer = a

    if best_score > 0.55:
        return best_answer

    return None

# =========================
# PROFILE SYSTEM
# =========================
def set_profile(key, value):
    cursor.execute("REPLACE INTO profile (key, value) VALUES (?, ?)", (key, value))
    conn.commit()

def get_profile(key):
    cursor.execute("SELECT value FROM profile WHERE key=?", (key,))
    row = cursor.fetchone()
    return row[0] if row else None

# =========================
# TOOLS
# =========================
def tools(text):
    if "/time" in text:
        return str(datetime.datetime.now().strftime("%H:%M:%S"))

    if "/date" in text:
        return str(datetime.date.today())

    if "/clear" in text:
        cursor.execute("DELETE FROM memory")
        conn.commit()
        return "Memory cleared"

    return None

# =========================
# BRAIN ENGINE
# =========================
def brain(text):
    text = text.lower()

    # tools first
    t = tools(text)
    if t:
        return t

    # profile
    if text.startswith("আমার নাম"):
        name = text.replace("আমার নাম", "").strip()
        set_profile("name", name)
        return f"আমি মনে রাখলাম তোমার নাম {name}"

    if "আমার নাম কি" in text:
        name = get_profile("name")
        return f"তোমার নাম {name}" if name else "আমি জানি না"

    # teach mode
    if text.startswith("শিখো"):
        try:
            parts = text.replace("শিখো", "").split("=")
            knowledge[parts[0].strip()] = parts[1].strip()
            return "আমি শিখে ফেলেছি"
        except:
            return "ফরম্যাট: শিখো key = value"

    # memory
    mem = smart_search(text)
    if mem:
        return mem

    # knowledge
    for k in knowledge:
        if k in text:
            return knowledge[k]

    if text in knowledge:
        return knowledge[text]

    return "আমি নিশ্চিত না, তুমি আমাকে শেখাতে পারো"

# =========================
# INPUT (VOICE)
# =========================
def listen():
    print("🎤 বলো...")
    os.system("termux-speech-to-text > input.txt")

    try:
        with open("input.txt", "r") as f:
            return f.read().strip()
    except:
        return ""

# =========================
# UI DASHBOARD
# =========================
def ui():
    os.system("clear")
    print("====================================")
    print(" 🚀 NexVoice AI OS v1 (FINAL)")
    print("====================================")
    print("Commands: /time /date /clear")
    print("Say anything...\n")
    print("------------------------------------")

    for c in chat_history[-6:]:
        print(c)

    print("====================================")

# =========================
# MAIN LOOP
# =========================
print("🚀 NexVoice AI OS v1 Started")

while True:
    ui()

    user = listen()

    if user == "":
        continue

    if "exit" in user.lower():
        speak("ঠিক আছে, আমি বন্ধ হচ্ছি")
        break

    answer = brain(user)

    save_memory(user, answer)

    chat_history.append(f"YOU: {user}")
    chat_history.append(f"AI: {answer}")

    print("YOU:", user)
    print("AI:", answer)

    speak(answer)
