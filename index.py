import os
import json
import asyncio
import edge_tts
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, Response

app = Flask(__name__)
app.secret_key = "messenger_clone_secret_123"

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
db_collection = None

if MONGO_URI:
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        db = client.messenger_video_maker
        db_collection = db.chat_data
    except Exception as e:
        print("MongoDB Error:", e)

# Default Data (Updated with Chat Mode)
fallback_data = {
    "pfp1": "https://i.pravatar.cc/150?img=11", 
    "pfp2": "https://i.pravatar.cc/150?img=5",  
    "name": "Reji Kabeer B",
    "chat_mode": "single", # 'single' or 'group'
    "messages": [
        {"sender": "time", "text": ""},
        {"sender": "1", "text": "Hey 👋"},
        {"sender": "time", "text": ""},
        {"sender": "2", "text": "Hi"}
    ]
}

# ================= VOICE MAPPING SYSTEM (20 VOICES) ================= #
# 1 = Boy (Me), 2 = Target (Female default)
VOICE_MAP = {"1": "bn-BD-PradeepNeural", "me": "bn-BD-PradeepNeural", "2": "bn-BD-NabanitaNeural"}
for i in range(1, 11):
    VOICE_MAP[f"b{i}"] = "bn-BD-PradeepNeural" if i % 2 != 0 else "bn-IN-BashkarNeural"
    VOICE_MAP[f"g{i}"] = "bn-BD-NabanitaNeural" if i % 2 != 0 else "bn-IN-TanishaaNeural"

def get_data():
    if db_collection is not None:
        data = db_collection.find_one({"_id": "main_chat"})
        if data: return data
    return fallback_data

def save_data(data):
    global fallback_data
    if db_collection is not None:
        db_collection.update_one({"_id": "main_chat"}, {"$set": data}, upsert=True)
    else:
        fallback_data = data

# ================= PWA SETUP (SHOWS REAL MOBILE STATUS BAR) ================= #
@app.route('/manifest.json')
def manifest():
    manifest_data = {
        "name": "Auto Chat Video",
        "short_name": "ChatVideo",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#ffffff",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/733/733548.png", "sizes": "192x192", "type": "image/png"},
            {"src": "https://cdn-icons-png.flaticon.com/512/733/733548.png", "sizes": "512x512", "type": "image/png"}
        ]
    }
    return Response(json.dumps(manifest_data), mimetype='application/json')

@app.route('/sw.js')
def service_worker():
    sw_code = """
    self.addEventListener('install', function(event) {
        self.skipWaiting();
    });
    self.addEventListener('fetch', function(event) {
        event.respondWith(fetch(event.request).catch(() => new Response("Offline")));
    });
    """
    return Response(sw_code, mimetype='application/javascript')

# ================= LIVE TTS AUDIO ROUTE (Fix for Vercel Sound Issue) ================= #
@app.route('/api/tts')
def api_tts():
    text = request.args.get('text', '')
    sender = request.args.get('sender', '1')
    if not text:
        return Response(b'', mimetype='audio/mpeg')

    voice = VOICE_MAP.get(sender, "bn-BD-PradeepNeural")

    async def get_audio_bytes():
        try:
            communicate = edge_tts.Communicate(text, voice)
            data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    data += chunk["data"]
            return data
        except:
            return b""

    audio_bytes = asyncio.run(get_audio_bytes())
    return Response(audio_bytes, mimetype="audio/mpeg")


# ================= HTML TEMPLATES (Your exact original code preserved) ================= #
CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Messenger Clone</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#EBF0F6">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        /* Global Reset */
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #000; display: flex; justify-content: center; height: 100dvh; overflow: hidden; }
        
        .messenger-container { 
            background: #EBF0F6; 
            width: 100%; max-width: 480px; height: 100dvh; 
            display: flex; flex-direction: column; position: relative; overflow: hidden;
        }
        
        /* New Messenger Chat Header */
        .header { 
            display: flex; align-items: center; padding: 12px 15px; 
            background-color: #EBF0F6; z-index: 10; border-bottom: 1px solid rgba(0,0,0,0.05); 
        }
        .icon-btn { background: transparent; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; margin-right: 5px; }
        .icon-btn svg { fill: #0084FF; width: 24px; height: 24px; }
        .profile-info { display: flex; align-items: center; flex: 1; margin-left: 10px; }
        .profile-img { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; }
        .user-name { font-size: 16px; margin-left: 10px; color: #000; font-weight: 600; }
        .header-actions { display: flex; gap: 15px; }

        /* Chat Area */
        .chat-area { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; padding-bottom: 20px; scroll-behavior: smooth;}
        .chat-area::-webkit-scrollbar { display: none; }
        
        /* Top Profile Banner */
        .top-profile { text-align: center; margin-bottom: 25px; margin-top: 10px; display: flex; flex-direction: column; align-items: center; }
        .top-profile img { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; }
        .top-profile h2 { font-size: 20px; margin-top: 10px; color: #000; font-weight: 600; }
        .top-profile p { font-size: 13px; color: #555; margin-top: 2px; }
        .btn-view-profile { background-color: rgba(0,0,0,0.05); border: none; padding: 7px 14px; border-radius: 6px; font-weight: 600; font-size: 14px; margin-top: 12px; cursor: pointer; }
        .security-notice { font-size: 11px; color: #65676B; margin-top: 15px; line-height: 1.4; padding: 0 15px; text-align: center; }
        .security-notice svg { width: 10px; height: 10px; fill: #65676B; margin-right: 2px; vertical-align: middle; }
        .security-notice span { color: #0084FF; font-weight: 600; }

        /* TIME & DATE STAMP CSS */
        .timestamp {
            text-align: center; font-size: 11px; color: #65676B; font-weight: 500;
            margin: 20px 0 10px 0; text-transform: uppercase; width: 100%;
        }

        /* Message Styling */
        .message-row { display: flex; margin-bottom: 2px; width: 100%; align-items: flex-end;}
        .message-row.me { justify-content: flex-end; }
        .message-row.them { justify-content: flex-start; }
        .them-pic { width: 24px; height: 24px; border-radius: 50%; margin-right: 8px; object-fit: cover;}
        
        .bubble { padding: 9px 15px; border-radius: 18px; font-size: 16px; max-width: 75%; word-wrap: break-word; line-height: 1.4; }
        .me .bubble { background-color: #0084ff; color: white; border-bottom-right-radius: 4px; }
        .them .bubble { background-color: rgba(0,0,0,0.05); color: black; border-bottom-left-radius: 4px; }
        
        /* 3 Dots Typing Indicator */
        .typing-bubble { background: rgba(0,0,0,0.05); padding: 12px 16px; border-radius: 18px; border-bottom-left-radius: 4px; display: flex; gap: 4px; align-items: center; width: fit-content; }
        .dot { width: 6px; height: 6px; background-color: #8D949E; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

        /* New Bottom Input Area */
        .input-area { display: flex; align-items: center; padding: 10px 12px; background-color: #EBF0F6; padding-bottom: 20px; z-index: 5;}
        .left-actions { display: flex; align-items: center; gap: 12px; margin-right: 12px; }
        .left-actions svg { fill: #0084FF; width: 26px; height: 26px; }
        .input-container { flex-grow: 1; background-color: rgba(0,0,0,0.05); border-radius: 20px; padding: 8px 15px; display: flex; align-items: center; }
        .input-box { border: none; background: transparent; outline: none; width: 100%; font-size: 16px; color: #050505; }
        .emoji-btn { background: transparent; border: none; display: flex; align-items: center; cursor: pointer; }
        .emoji-btn svg { fill: #0084FF; width: 22px; height: 22px; margin-left: 5px; }
        
        .input-right-icon { color: #0084ff; font-size: 26px; margin-left: 12px; transition: 0.2s; cursor: pointer; }

        /* Gboard Keyboard */
        .keyboard-area { 
            height: 0; background: #18191c; transition: height 0.25s cubic-bezier(0, 0, 0.2, 1); 
            overflow: hidden; display: flex; flex-direction: column; justify-content: flex-end; 
            position: relative; padding: 0 3px 6px 3px; user-select: none; -webkit-user-select: none; 
            border-top: 1px solid #23252a;
        }
        .keyboard-area.active { height: 295px; }
        .gboard-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 6px 14px 6px 14px; color: #9aa0a6; font-size: 15px; background: #18191c; }
        .gboard-toolbar .tool-icons { display: flex; align-items: center; gap: 18px; }
        .kb-row { display: flex; gap: 5px; margin-bottom: 6px; justify-content: center; width: 100%; padding: 0 2px; }
        .kb-key { background: #2c2e33; color: #ffffff; border-radius: 6px; height: 44px; flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 17px; font-weight: 400; position: relative; box-shadow: 0 1.5px 2px rgba(0,0,0,0.35); transition: background 0.08s ease, transform 0.08s ease; }
        .kb-key .hint { position: absolute; top: 2px; right: 4px; font-size: 9px; color: #8c9096; font-weight: 500; }
        .kb-key.special { background: #202225; flex: 1.4; color: #d1d5db; font-size: 14px; }
        .kb-key.space-key { flex: 4.8; font-size: 13px; color: #9aa0a6; display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 6px; }
        .kb-key.enter-key { background: #202225; flex: 1.4; color: #ffffff; }
        .kb-key.pressed { background: #4e535c !important; color: #fff !important; transform: scale(0.92); }

        /* Overlays */
        .overlay-start { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.92); display: flex; justify-content: center; align-items: center; z-index: 100; flex-direction: column; color: white;}
        .start-btn { background: #0084ff; color: white; padding: 14px 28px; font-size: 17px; border: none; border-radius: 25px; cursor: pointer; margin-top: 15px; font-weight: 600; box-shadow: 0 4px 10px rgba(0,132,255,0.4);}
        .seen-indicator { width: 14px; height: 14px; border-radius: 50%; object-fit: cover; align-self: flex-end; margin-top: 4px; display: none; margin-right: 4px; }
    </style>
</head>
<body>

<div class="messenger-container" id="messenger">
    <!-- Start Recording Overlay -->
    <div class="overlay-start" id="overlay">
        <h2 style="margin-bottom: 8px;">Ready to Start</h2>
        <p style="text-align:center; padding: 0 20px; font-size: 13px; color:#ccc; line-height: 1.5;">
            স্টার্ট বাটনে চাপ দিলে স্ক্রিন ৩ সেকেন্ড স্থির থাকবে,<br>
            যাতে আপনি সহজে ভিডিও রেকর্ড ও কাট করতে পারেন।
        </p>
        <button class="start-btn" onclick="startAutoChat()">Start Chat</button>
    </div>

    <!-- Messenger Header -->
    <div class="header">
        <button class="icon-btn">
            <svg viewBox="0 0 24 24"><path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/></svg>
        </button>
        <div class="profile-info">
            <img src="" id="header-pfp" class="profile-img" alt="PFP">
            <span class="user-name" id="chat-name">Name</span>
        </div>
        <div class="header-actions">
            <button class="icon-btn">
                <svg viewBox="0 0 24 24"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
            </button>
            <button class="icon-btn">
                <svg viewBox="0 0 24 24"><path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/></svg>
            </button>
        </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-area" id="chat-area">
        <div class="top-profile">
            <img src="" id="top-pfp" alt="Profile Big">
            <h2 id="top-name">Name</h2>
            <p>You're friends on Facebook</p>
            <button class="btn-view-profile">View profile</button>
            <p class="security-notice">
                <svg viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm9 14H6V10h12v10zm-6-3c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/></svg>
                Messages and calls are secured with end-to-end encryption. Only people in this chat can read, listen to, or share them. <span>Learn more</span>
            </p>
        </div>

        <div class="message-row them" id="typing-row" style="display: none;">
            <img src="" id="typing-pfp" class="them-pic">
            <div class="typing-bubble">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>
        </div>
        <div style="display:flex; justify-content: flex-end;">
            <img src="" id="seen-pfp" class="seen-indicator">
        </div>
    </div>

    <!-- Bottom Input Area -->
    <div class="input-area">
        <div class="left-actions">
            <button class="icon-btn"><svg viewBox="0 0 24 24"><path d="M4 4h3l2-2h6l2 2h3c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm8 3c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.65 0-3-1.35-3-3s1.35-3 3-3 3 1.35 3 3-1.35 3-3 3z"/></svg></button>
            <button class="icon-btn"><svg viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg></button>
            <button class="icon-btn"><svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/></svg></button>
        </div>
        
        <div class="input-container">
            <input type="text" class="input-box" id="msg-input" placeholder="Aa" readonly>
            <button class="emoji-btn"><svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 8c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm-7 0c.83 0 1.5.67 1.5 1.5S9.33 13 8.5 13 7 12.33 7 11.5 7.67 10 8.5 10zm3.5 8c-2.33 0-4.31-1.46-5.11-3.5h10.22c-.8 2.04-2.78 3.5-5.11 3.5z"/></svg></button>
        </div>
        
        <i class="fa-solid fa-thumbs-up input-right-icon" id="send-icon"></i>
    </div>

    <!-- Gboard Keyboard -->
    <div class="keyboard-area" id="keyboard">
        <div class="gboard-toolbar">
            <div class="tool-icons">
                <i class="fa-solid fa-chevron-right"></i>
                <i class="fa-regular fa-face-smile"></i>
                <i class="fa-solid fa-wand-magic-sparkles"></i>
                <i class="fa-solid fa-gear"></i>
                <i class="fa-solid fa-ellipsis"></i>
            </div>
            <i class="fa-solid fa-microphone"></i>
        </div>
        <div class="kb-row" id="kb-r1"></div>
        <div class="kb-row" id="kb-r2"></div>
        <div class="kb-row" id="kb-r3"></div>
        <div class="kb-row" id="kb-r4"></div>
    </div>
</div>

<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js');
    }

    let chatData = {};
    fetch('/api/get_data').then(res => res.json()).then(data => {
        chatData = data;
        document.getElementById('header-pfp').src = data.pfp2;
        document.getElementById('typing-pfp').src = data.pfp2;
        document.getElementById('seen-pfp').src = data.pfp2;
        document.getElementById('chat-name').innerText = data.name;
        document.getElementById('top-pfp').src = data.pfp2;
        document.getElementById('top-name').innerText = data.name;
    });

    function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

    const gboardLayouts = {
        'BN': {
            langLabel: '◀ প্রভাত ▶',
            rows: [
                [{c: 'দ', h: '১'}, {c: 'ূ', h: '২'}, {c: 'ী', h: '৩'}, {c: 'র', h: '৪'}, {c: 'ট', h: '৫'}, {c: 'এ', h: '৬'}, {c: 'ি', h: '৭'}, {c: 'ও', h: '৮'}, {c: 'প', h: '৯'}, {c: 'চ', h: '০'}],
                [{c: 'া', h: '@'}, {c: 'স', h: '#'}, {c: 'ড', h: '৳'}, {c: 'ত', h: '%'}, {c: 'গ', h: '&'}, {c: 'হ', h: '-'}, {c: 'জ', h: '+'}, {c: 'ক', h: '('}, {c: 'ল', h: ')'}, {c: 'ে', h: '='}],
                [{type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'}, {c: 'য়'}, {c: 'শ'}, {c: 'ু'}, {c: 'আ'}, {c: 'ব'}, {c: 'ন'}, {c: 'ম'}, {c: 'ো'}, {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}],
                [{type: 'special', text: '?123'}, {c: ',', h: '☺'}, {type: 'space', text: '◀ প্রভাত ▶'}, {c: '।'}, {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}]
            ]
        },
        'EN': {
            langLabel: '◀ English ▶',
            rows: [
                [{c: 'q', h: '1'}, {c: 'w', h: '2'}, {c: 'e', h: '3'}, {c: 'r', h: '4'}, {c: 't', h: '5'}, {c: 'y', h: '6'}, {c: 'u', h: '7'}, {c: 'i', h: '8'}, {c: 'o', h: '9'}, {c: 'p', h: '0'}],
                [{c: 'a', h: '@'}, {c: 's', h: '#'}, {c: 'd', h: '$'}, {c: 'f', h: '_'}, {c: 'g', h: '&'}, {c: 'h', h: '-'}, {c: 'j', h: '+'}, {c: 'k', h: '('}, {c: 'l', h: ')'}],
                [{type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'}, {c: 'z'}, {c: 'x'}, {c: 'c'}, {c: 'v'}, {c: 'b'}, {c: 'n'}, {c: 'm'}, {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}],
                [{type: 'special', text: '?123'}, {c: ',', h: '☺'}, {type: 'space', text: '◀ English ▶'}, {c: '.'}, {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}]
            ]
        },
        'AR': {
            langLabel: '◀ العربية ▶',
            rows: [
                [{c: 'ض', h: '١'}, {c: 'ص', h: '٢'}, {c: 'ث', h: '٣'}, {c: 'ق', h: '٤'}, {c: 'ف', h: '٥'}, {c: 'غ', h: '٦'}, {c: 'ع', h: '٧'}, {c: 'ه', h: '٨'}, {c: 'خ', h: '٩'}, {c: 'ح', h: '٠'}, {c: 'ج'}, {c: 'د'}],
                [{c: 'ش'}, {c: 'س'}, {c: 'ي'}, {c: 'ب'}, {c: 'ل'}, {c: 'ا'}, {c: 'ت'}, {c: 'ن'}, {c: 'م'}, {c: 'ك'}, {c: 'ط'}],
                [{type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'}, {c: 'ئ'}, {c: 'ء'}, {c: 'ؤ'}, {c: 'ر'}, {c: 'لا'}, {c: 'ى'}, {c: 'ة'}, {c: 'و'}, {c: 'ز'}, {c: 'ظ'}, {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}],
                [{type: 'special', text: '?123'}, {c: '،'}, {type: 'space', text: '◀ العربية ▶'}, {c: '.'}, {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}]
            ]
        }
    };

    function detectScript(text) {
        for (let ch of text) {
            const code = ch.charCodeAt(0);
            if (code >= 0x0980 && code <= 0x09FF) return 'BN';
            if (code >= 0x0600 && code <= 0x06FF) return 'AR';
            if (ch > '~') return 'GLOBAL';
        }
        return 'EN';
    }

    function renderGboard(text) {
        const lang = detectScript(text);
        let layout = gboardLayouts[lang];

        if (!layout) {
            const unique = Array.from(new Set(text.replace(/\\s/g, '')));
            const r1 = [], r2 = [], r3 = [];
            unique.forEach((c, i) => {
                const target = i % 3 === 0 ? r1 : (i % 3 === 1 ? r2 : r3);
                target.push({c: c, h: (i % 9 + 1).toString()});
            });
            while(r1.length < 10) r1.push({c: '•', h: ''});
            while(r2.length < 9) r2.push({c: '•', h: ''});
            while(r3.length < 7) r3.push({c: '•', h: ''});

            layout = {
                langLabel: '◀ Global ▶',
                rows: [
                    r1, r2,
                    [{type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'}, ...r3, {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}],
                    [{type: 'special', text: '?123'}, {c: ','}, {type: 'space', text: '◀ Global ▶'}, {c: '.'}, {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}]
                ]
            };
        }

        for (let r = 1; r <= 4; r++) {
            const rowElem = document.getElementById(`kb-r${r}`);
            rowElem.innerHTML = '';
            layout.rows[r - 1].forEach(item => {
                const key = document.createElement('div');
                key.className = 'kb-key';

                if (item.type === 'special') {
                    key.classList.add('special'); key.innerHTML = item.icon || item.text;
                } else if (item.type === 'space') {
                    key.classList.add('space-key'); key.innerHTML = item.text;
                } else if (item.type === 'enter') {
                    key.classList.add('enter-key'); key.innerHTML = item.icon;
                } else {
                    key.setAttribute('data-char', item.c);
                    key.innerHTML = `${item.c}${item.h ? `<span class="hint">${item.h}</span>` : ''}`;
                }
                rowElem.appendChild(key);
            });
        }
    }

    async function simulateTypingKeyboard(text) {
        const kb = document.getElementById('keyboard');
        renderGboard(text);
        kb.classList.add('active'); 
        await sleep(350);

        const input = document.getElementById('msg-input');
        const icon = document.getElementById('send-icon');
        icon.classList.remove('fa-thumbs-up'); 
        icon.classList.add('fa-paper-plane');
        
        const chars = Array.from(text);
        for (let i = 0; i < chars.length; i++) {
            const ch = chars[i];
            input.value += ch;

            let targetKey = document.querySelector(`.kb-key[data-char="${ch}"]`);
            if (!targetKey && ch === ' ') targetKey = document.querySelector('.kb-key.space-key');
            if (!targetKey) {
                const normalKeys = document.querySelectorAll('.kb-key[data-char]');
                if (normalKeys.length > 0) targetKey = normalKeys[Math.floor(Math.random() * normalKeys.length)];
            }
            if (targetKey) {
                targetKey.classList.add('pressed');
                setTimeout(() => targetKey.classList.remove('pressed'), 110);
            }
            await sleep(130); 
        }
        await sleep(400); 
        input.value = "";
        icon.classList.remove('fa-paper-plane'); 
        icon.classList.add('fa-thumbs-up');
        kb.classList.remove('active'); 
        await sleep(250);
    }

    function scrollToBottom() {
        const chat = document.getElementById('chat-area');
        chat.scrollTop = chat.scrollHeight;
    }

    function getMessengerTime() {
        const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
        const now = new Date();
        const month = months[now.getMonth()];
        const date = now.getDate();
        let hours = now.getHours();
        let minutes = now.getMinutes();
        minutes = minutes < 10 ? '0' + minutes : minutes;
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        return `${month} ${date} AT ${hours}:${minutes} ${ampm}`;
    }

    // NEW PLAY AUDIO LOGIC
    async function playAudio(text, sender) {
        if(!text) return;
        let audioUrl = `/api/tts?text=${encodeURIComponent(text)}&sender=${sender}`;
        let audio = new Audio(audioUrl);
        return new Promise((resolve) => {
            audio.onended = resolve;
            audio.onerror = resolve;
            audio.play().catch(e => resolve());
        });
    }

    // DYNAMIC APPEND FUNCTION (Handles both Single & Group Modes perfectly)
    function appendMessage(text, sender) {
        const div = document.createElement('div');
        
        if (sender === "time") {
            div.className = 'timestamp';
            div.innerText = text;
        } else if (chatData.chat_mode === "group") {
            // == GROUP CHAT MODE ==
            div.style.display = 'flex'; div.style.flexDirection = 'column'; div.style.marginBottom = '4px'; div.style.width = '100%';
            if (sender === "1" || sender === "me") {
                div.innerHTML = `<div class="message-row me"><div class="bubble">${text}</div></div>`;
            } else {
                let name = sender.startsWith('b') ? 'Boy ' + sender.replace('b','') : sender.startsWith('g') ? 'Girl ' + sender.replace('g','') : 'Target';
                let pfp = sender === '2' ? chatData.pfp2 : sender.startsWith('b') ? `https://i.pravatar.cc/150?img=${10+parseInt(sender.replace('b',''))}` : `https://i.pravatar.cc/150?img=${30+parseInt(sender.replace('g',''))}`;
                
                div.innerHTML = `
                    <span style="font-size:11px;color:#65676B;margin-left:45px;margin-bottom:3px;display:block;">${name}</span>
                    <div class="message-row them">
                        <img src="${pfp}" class="them-pic" style="width:28px;height:28px;border-radius:50%;margin-right:8px;object-fit:cover;align-self:flex-end;">
                        <div class="bubble">${text}</div>
                    </div>`;
            }
        } else {
            // == SINGLE CHAT MODE (YOUR EXACT ORIGINAL CODE) ==
            if (sender === "1" || sender === "me") {
                div.className = 'message-row me';
                div.innerHTML = `<div class="bubble">${text}</div>`;
            } else {
                div.className = 'message-row them';
                div.innerHTML = `<img src="${chatData.pfp2}" class="them-pic"><div class="bubble">${text}</div>`;
            }
        }
        
        document.getElementById('chat-area').insertBefore(div, document.getElementById('typing-row'));
        scrollToBottom();
    }

    async function startAutoChat() {
        document.getElementById('overlay').style.display = 'none';
        await sleep(3000);

        for (let msg of chatData.messages) {
            if (msg.sender === "time") {
                let timeText = msg.text.trim();
                if (!timeText) timeText = getMessengerTime();
                appendMessage(timeText, "time");
            } else if (msg.sender === "1" || msg.sender === "me") {
                await simulateTypingKeyboard(msg.text); 
                appendMessage(msg.text, msg.sender);
                await playAudio(msg.text, msg.sender); // Play sound
                await sleep(500);
            } else {
                // Change Typing Indicator PFP based on mode
                if (chatData.chat_mode === "group") {
                    let pfp = msg.sender === '2' ? chatData.pfp2 : msg.sender.startsWith('b') ? `https://i.pravatar.cc/150?img=${10+parseInt(msg.sender.replace('b',''))}` : `https://i.pravatar.cc/150?img=${30+parseInt(msg.sender.replace('g',''))}`;
                    document.getElementById('typing-pfp').src = pfp;
                } else {
                    document.getElementById('typing-pfp').src = chatData.pfp2;
                }
                
                document.getElementById('typing-row').style.display = 'flex'; 
                scrollToBottom();
                await sleep(msg.text.length * 60 + 1000); 
                document.getElementById('typing-row').style.display = 'none'; 
                
                appendMessage(msg.text, msg.sender);
                await playAudio(msg.text, msg.sender); // Play sound
                await sleep(500);
            }
            document.getElementById('seen-pfp').style.display = 'none'; 
        }
        
        document.getElementById('seen-pfp').style.display = 'block';
        scrollToBottom();
    }
</script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - Auto Chat</title><script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-5">
    <div class="max-w-3xl mx-auto bg-white p-6 rounded-lg shadow-md">
        <div class="flex justify-between items-center border-b pb-3 mb-4">
            <h2 class="text-2xl font-bold text-blue-600">Admin Panel (Chat Setup)</h2>
            <a href="/" target="_blank" class="bg-green-500 text-white px-4 py-2 rounded">View Chat</a>
        </div>
        <form id="chatForm">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div><label class="block font-bold mb-1">My Profile Picture URL</label><input type="text" id="pfp1" class="w-full border p-2 rounded" required></div>
                <div><label class="block font-bold mb-1">Target Profile Picture URL</label><input type="text" id="pfp2" class="w-full border p-2 rounded" required></div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div><label class="block font-bold mb-1">Chat Header Name</label><input type="text" id="chatName" class="w-full border p-2 rounded" required></div>
                <div>
                    <label class="block font-bold mb-1 text-red-600">Chat Mode System</label>
                    <select id="chatMode" class="w-full border p-2 rounded font-bold">
                        <option value="single">Single Chat (1 on 1)</option>
                        <option value="group">Group Chat (Multiple Peoples)</option>
                    </select>
                </div>
            </div>
            
            <!-- NEW HTML IMPORT SYSTEM -->
            <div class="mb-4 bg-gray-50 p-4 rounded border border-gray-200">
                <label class="block font-bold mb-1 text-blue-700">Import Messages from HTML</label>
                <p class="text-xs text-gray-500 mb-2">গল্পের স্ক্রিপ্ট একবারে সেট করতে এখানে HTML পেস্ট করুন। আপনার মেসেজে class="me", তার মেসেজে class="he" বা "she", গ্রুপ হলে class="b1" বা "g2" এবং সময়ের জন্য class="time" ব্যবহার করুন।</p>
                <textarea id="htmlInput" class="w-full border p-2 rounded mb-2" rows="4" placeholder='<div class="me">Hello</div>&#10;<div class="he">Hi</div>'></textarea>
                <button type="button" onclick="parseHTML()" class="bg-blue-500 text-white px-4 py-2 rounded shadow hover:bg-blue-600 font-bold">Import HTML</button>
            </div>

            <div class="mb-4">
                <h3 class="font-bold text-lg mb-2 border-b pb-1">Messages & Timestamps</h3>
                <div id="messages-container"></div>
                <button type="button" onclick="addMsgRow()" class="mt-3 bg-blue-100 text-blue-700 px-3 py-1 rounded shadow">+ Add Message</button>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg font-bold text-lg hover:bg-blue-700">Save Setup</button>
        </form>
    </div>
<script>
    let container = document.getElementById('messages-container');
    
    function getSenderOptions(selected) {
        let opts = `<option value="time" ${selected=='time'?'selected':''}>⌚ Time</option>
                    <option value="1" ${selected=='1' || selected=='me'?'selected':''}>👤 Me (You)</option>
                    <option value="2" ${selected=='2'?'selected':''}>👤 Them (Target)</option>`;
        for(let i=1; i<=10; i++) opts += `<option value="b${i}" ${selected==`b${i}`?'selected':''}>👦 Boy ${i}</option>`;
        for(let i=1; i<=10; i++) opts += `<option value="g${i}" ${selected==`g${i}`?'selected':''}>👧 Girl ${i}</option>`;
        return opts;
    }

    function addMsgRow(sender="1", text="") {
        const div = document.createElement('div'); div.className = "flex gap-2 mb-2 items-center";
        
        div.innerHTML = `<select class="border p-2 rounded w-1/4 msg-sender">
            ${getSenderOptions(sender)}
        </select>
        <input type="text" class="border p-2 rounded w-3/4 msg-text" value="${text}" placeholder="Type text or leave blank for Auto Real Time..." ${sender==="time"?"":"required"}>
        <button type="button" onclick="this.parentElement.remove()" class="bg-red-500 text-white px-3 py-2 rounded">X</button>`;
        
        div.querySelector('.msg-sender').addEventListener('change', function(e) {
            if(e.target.value === 'time') {
                div.querySelector('.msg-text').removeAttribute('required');
            } else {
                div.querySelector('.msg-text').setAttribute('required', 'true');
            }
        });

        container.appendChild(div);
    }

    // HTML Parse Function
    function parseHTML() {
        const val = document.getElementById('htmlInput').value;
        if(!val.trim()) return alert("দয়া করে আগে বক্সে HTML পেস্ট করুন!");
        
        const temp = document.createElement('div');
        temp.innerHTML = val;
        
        Array.from(temp.children).forEach(el => {
            const c = (el.className || '').toLowerCase();
            const txt = (el.innerText || el.textContent).trim();
            
            if(c.includes('me') || c === '1') {
                addMsgRow('1', txt);
            } else if(c.includes('he') || c.includes('she') || c.includes('them') || c === '2') {
                addMsgRow('2', txt);
            } else if(c.includes('time')) {
                addMsgRow('time', txt);
            } else if(c.match(/^[bg]\d+$/)) {
                addMsgRow(c, txt);
            } else {
                addMsgRow('1', txt);
            }
        });
        
        document.getElementById('htmlInput').value = '';
    }

    fetch('/api/get_data').then(r=>r.json()).then(data => {
        document.getElementById('pfp1').value = data.pfp1 || ""; 
        document.getElementById('pfp2').value = data.pfp2 || ""; 
        document.getElementById('chatName').value = data.name || "Unknown";
        document.getElementById('chatMode').value = data.chat_mode || "single";
        
        if(data.messages) data.messages.forEach(m => addMsgRow(m.sender, m.text)); else addMsgRow();
    });
    
    document.getElementById('chatForm').onsubmit = function(e) {
        e.preventDefault(); let msgs = [];
        document.querySelectorAll('#messages-container > div').forEach(row => { msgs.push({sender: row.querySelector('.msg-sender').value, text: row.querySelector('.msg-text').value}); });
        
        fetch('/api/save_data', { 
            method: 'POST', 
            headers: {'Content-Type': 'application/json'}, 
            body: JSON.stringify({
                pfp1: document.getElementById('pfp1').value, 
                pfp2: document.getElementById('pfp2').value, 
                name: document.getElementById('chatName').value, 
                chat_mode: document.getElementById('chatMode').value,
                messages: msgs
            }) 
        }).then(() => alert("Chat setup saved successfully!"));
    };
</script>
</body></html>
"""

LOGIN_HTML = """
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Admin Login</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-200 flex items-center justify-center h-screen"><div class="bg-white p-8 rounded shadow-lg max-w-sm w-full"><h2 class="text-2xl font-bold mb-5 text-center">Admin Login</h2><form method="POST"><input type="password" name="password" placeholder="Password" class="w-full border p-2 mb-4 rounded" required><button class="w-full bg-blue-600 text-white py-2 rounded font-bold">Login</button></form><p class="text-center text-gray-500 mt-4 text-sm">Default Password: <strong>admin123</strong></p></div></body></html>
"""

# ================= FLASK ROUTES ================= #

@app.route("/")
def index(): return render_template_string(CHAT_HTML)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == "admin123":
            session["logged_in"] = True
            return redirect(url_for("admin"))
        return "Wrong password", 401
    if not session.get("logged_in"): return render_template_string(LOGIN_HTML)
    return render_template_string(ADMIN_HTML)

@app.route("/api/get_data", methods=["GET"])
def api_get():
    data = get_data()
    if "_id" in data: del data["_id"]
    return jsonify(data)

@app.route("/api/save_data", methods=["POST"])
def api_save():
    if not session.get("logged_in"): return jsonify({"error": "Unauthorized"}), 401
    save_data(request.json)
    return jsonify({"success": True})

application = app
if __name__ == "__main__": app.run(debug=True)
