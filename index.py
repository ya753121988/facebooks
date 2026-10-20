import os
import json
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
    except:
        pass

# Default Data
fallback_data = {
    "pfp1": "https://i.pravatar.cc/150?img=11", 
    "pfp2": "https://i.pravatar.cc/150?img=5",  
    "name": "Mark Zuckerberg",
    "messages": [
        {"sender": "1", "text": "হ্যালো মার্ক! কেমন আছো? তুমি কি ভালো?"},
        {"sender": "2", "text": "Hi! I am good. How are you?"}
    ]
}

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
            {
                "src": "https://cdn-icons-png.flaticon.com/512/733/733548.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/733/733548.png",
                "sizes": "512x512",
                "type": "image/png"
            }
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

# ================= HTML TEMPLATES ================= #

CHAT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Messenger Clone</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#ffffff">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            background-color: #000; 
            display: flex; 
            justify-content: center; 
            height: 100dvh; 
            overflow: hidden; 
        }
        .messenger-container { 
            background: #fff; 
            width: 100%; 
            max-width: 480px; 
            height: 100dvh; 
            display: flex; 
            flex-direction: column; 
            position: relative; 
            overflow: hidden;
        }
        
        /* Messenger Chat Header */
        .header { 
            display: flex; 
            align-items: center; 
            justify-content: space-between; 
            padding: 10px 15px; 
            border-bottom: 1px solid #e0e0e0; 
            z-index: 10; 
            background: #fff;
        }
        .header-left { display: flex; align-items: center; gap: 12px; }
        .back-btn { color: #0084ff; font-size: 20px; cursor: pointer; }
        .pfp-container { position: relative; width: 40px; height: 40px; }
        .profile-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .active-dot { position: absolute; bottom: 0; right: 0; width: 11px; height: 11px; background-color: #31a24c; border: 2px solid #fff; border-radius: 50%; }
        
        .user-info { display: flex; flex-direction: column; }
        .user-name { font-weight: 600; font-size: 16px; color: #050505; }
        .active-status { font-size: 12px; color: #65676B; }
        .header-icons i { color: #0084ff; font-size: 19px; margin-left: 16px; cursor: pointer;}

        /* Chat Area */
        .chat-area { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; background: #ffffff; padding-bottom: 15px;}
        .message-row { display: flex; margin-bottom: 12px; width: 100%; align-items: flex-end;}
        .message-row.me { justify-content: flex-end; }
        .message-row.them { justify-content: flex-start; }
        
        .them-pic { width: 28px; height: 28px; border-radius: 50%; margin-right: 8px; object-fit: cover;}
        .bubble { max-width: 72%; padding: 10px 14px; border-radius: 18px; font-size: 15px; word-wrap: break-word; line-height: 1.4; }
        .me .bubble { background: #0084ff; color: white; border-bottom-right-radius: 4px; }
        .them .bubble { background: #e4e6eb; color: black; border-bottom-left-radius: 4px; }
        
        /* 3 Dots Typing Indicator */
        .typing-bubble { background: #e4e6eb; padding: 12px 16px; border-radius: 18px; border-bottom-left-radius: 4px; display: flex; gap: 4px; align-items: center; width: fit-content; }
        .dot { width: 6px; height: 6px; background-color: #8D949E; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

        /* Input Area */
        .input-area { display: flex; align-items: center; padding: 8px 10px; border-top: 1px solid #e0e0e0; background: #fff; z-index: 5;}
        .input-icons i { color: #0084ff; font-size: 20px; margin-right: 10px; }
        .input-box { flex: 1; background: #f0f2f5; border-radius: 20px; padding: 8px 14px; font-size: 15px; border: none; outline: none; }
        .input-right-icon { color: #0084ff; font-size: 20px; margin-left: 10px; transition: 0.2s;}

        /* Gboard Keyboard */
        .keyboard-area { 
            height: 0; 
            background: #18191c; 
            transition: height 0.25s cubic-bezier(0, 0, 0.2, 1); 
            overflow: hidden; 
            display: flex; 
            flex-direction: column; 
            justify-content: flex-end; 
            position: relative; 
            padding: 0 3px 6px 3px;
            user-select: none;
            -webkit-user-select: none;
            border-top: 1px solid #23252a;
        }
        .keyboard-area.active { 
            height: 295px; 
        }

        .gboard-toolbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 14px 6px 14px;
            color: #9aa0a6;
            font-size: 15px;
            background: #18191c;
        }
        .gboard-toolbar .tool-icons {
            display: flex;
            align-items: center;
            gap: 18px;
        }

        .kb-row { 
            display: flex; 
            gap: 5px; 
            margin-bottom: 6px; 
            justify-content: center; 
            width: 100%;
            padding: 0 2px;
        }
        .kb-key { 
            background: #2c2e33; 
            color: #ffffff;
            border-radius: 6px; 
            height: 44px;
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 17px;
            font-weight: 400;
            position: relative;
            box-shadow: 0 1.5px 2px rgba(0,0,0,0.35);
            transition: background 0.08s ease, transform 0.08s ease;
        }
        .kb-key .hint {
            position: absolute;
            top: 2px;
            right: 4px;
            font-size: 9px;
            color: #8c9096;
            font-weight: 500;
        }
        .kb-key.special {
            background: #202225;
            flex: 1.4;
            color: #d1d5db;
            font-size: 14px;
        }
        .kb-key.space-key {
            flex: 4.8;
            font-size: 13px;
            color: #9aa0a6;
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .kb-key.enter-key {
            background: #202225;
            flex: 1.4;
            color: #ffffff;
        }
        .kb-key.pressed { 
            background: #4e535c !important; 
            color: #fff !important;
            transform: scale(0.92); 
        }

        /* Overlays */
        .overlay-start { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.92); display: flex; justify-content: center; align-items: center; z-index: 100; flex-direction: column; color: white;}
        .start-btn { background: #0084ff; color: white; padding: 14px 28px; font-size: 17px; border: none; border-radius: 25px; cursor: pointer; margin-top: 15px; font-weight: 600; box-shadow: 0 4px 10px rgba(0,132,255,0.4);}
        .seen-indicator { width: 14px; height: 14px; border-radius: 50%; object-fit: cover; align-self: flex-end; margin-top: 4px; display: none; }
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

    <!-- Messenger Header (Mobile's Real Status Bar will show on top naturally) -->
    <div class="header">
        <div class="header-left">
            <i class="fa-solid fa-arrow-left back-btn"></i>
            <div class="pfp-container">
                <img src="" id="header-pfp" class="profile-img" alt="PFP">
                <div class="active-dot"></div>
            </div>
            <div class="user-info">
                <span class="user-name" id="chat-name">Name</span>
                <span class="active-status">Active Now</span>
            </div>
        </div>
        <div class="header-icons">
            <i class="fa-solid fa-phone"></i>
            <i class="fa-solid fa-video"></i>
            <i class="fa-solid fa-circle-info"></i>
        </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-area" id="chat-area">
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
        <div class="input-icons">
            <i class="fa-solid fa-circle-plus"></i>
            <i class="fa-solid fa-camera"></i>
            <i class="fa-solid fa-image"></i>
            <i class="fa-solid fa-microphone"></i>
        </div>
        <input type="text" class="input-box" id="msg-input" placeholder="Message" readonly>
        <i class="fa-solid fa-thumbs-up input-right-icon" id="send-icon"></i>
    </div>

    <!-- Gboard Keyboard (Real Dark Layout matching Screenshot) -->
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
    });

    function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

    // REAL GBOARD LAYOUTS
    const gboardLayouts = {
        'BN': {
            langLabel: '◀ প্রভাত ▶',
            rows: [
                [
                    {c: 'দ', h: '১'}, {c: 'ূ', h: '২'}, {c: 'ী', h: '৩'}, {c: 'র', h: '৪'}, {c: 'ট', h: '৫'}, 
                    {c: 'এ', h: '৬'}, {c: 'ি', h: '৭'}, {c: 'ও', h: '৮'}, {c: 'প', h: '৯'}, {c: 'চ', h: '০'}
                ],
                [
                    {c: 'া', h: '@'}, {c: 'স', h: '#'}, {c: 'ড', h: '৳'}, {c: 'ত', h: '%'}, {c: 'গ', h: '&'}, 
                    {c: 'হ', h: '-'}, {c: 'জ', h: '+'}, {c: 'ক', h: '('}, {c: 'ল', h: ')'}, {c: 'ে', h: '='}
                ],
                [
                    {type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'},
                    {c: 'য়'}, {c: 'শ'}, {c: 'ু'}, {c: 'আ'}, {c: 'ব'}, {c: 'ন'}, {c: 'ম'}, {c: 'ো'},
                    {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}
                ],
                [
                    {type: 'special', text: '?123'},
                    {c: ',', h: '☺'},
                    {type: 'space', text: '◀ প্রভাত ▶'},
                    {c: '।'},
                    {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}
                ]
            ]
        },
        'EN': {
            langLabel: '◀ English ▶',
            rows: [
                [
                    {c: 'q', h: '1'}, {c: 'w', h: '2'}, {c: 'e', h: '3'}, {c: 'r', h: '4'}, {c: 't', h: '5'}, 
                    {c: 'y', h: '6'}, {c: 'u', h: '7'}, {c: 'i', h: '8'}, {c: 'o', h: '9'}, {c: 'p', h: '0'}
                ],
                [
                    {c: 'a', h: '@'}, {c: 's', h: '#'}, {c: 'd', h: '$'}, {c: 'f', h: '_'}, {c: 'g', h: '&'}, 
                    {c: 'h', h: '-'}, {c: 'j', h: '+'}, {c: 'k', h: '('}, {c: 'l', h: ')'}
                ],
                [
                    {type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'},
                    {c: 'z'}, {c: 'x'}, {c: 'c'}, {c: 'v'}, {c: 'b'}, {c: 'n'}, {c: 'm'},
                    {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}
                ],
                [
                    {type: 'special', text: '?123'},
                    {c: ',', h: '☺'},
                    {type: 'space', text: '◀ English ▶'},
                    {c: '.'},
                    {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}
                ]
            ]
        },
        'AR': {
            langLabel: '◀ العربية ▶',
            rows: [
                [
                    {c: 'ض', h: '١'}, {c: 'ص', h: '٢'}, {c: 'ث', h: '٣'}, {c: 'ق', h: '٤'}, {c: 'ف', h: '٥'}, 
                    {c: 'غ', h: '٦'}, {c: 'ع', h: '٧'}, {c: 'ه', h: '٨'}, {c: 'خ', h: '٩'}, {c: 'ح', h: '٠'}, {c: 'ج'}, {c: 'د'}
                ],
                [
                    {c: 'ش'}, {c: 'س'}, {c: 'ي'}, {c: 'ব'}, {c: 'ل'}, {c: 'ا'}, {c: 'ت'}, {c: 'ن'}, {c: 'ম'}, {c: 'ك'}, {c: 'ط'}
                ],
                [
                    {type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'},
                    {c: 'ئ'}, {c: 'ء'}, {c: 'ؤ'}, {c: 'ر'}, {c: 'لا'}, {c: 'ى'}, {c: 'ة'}, {c: 'و'}, {c: 'ز'}, {c: 'ظ'},
                    {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}
                ],
                [
                    {type: 'special', text: '?123'},
                    {c: '،'},
                    {type: 'space', text: '◀ العربية ▶'},
                    {c: '.'},
                    {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}
                ]
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
                    r1,
                    r2,
                    [{type: 'special', icon: '<i class="fa-solid fa-arrow-up"></i>'}, ...r3, {type: 'special', icon: '<i class="fa-solid fa-delete-left"></i>'}],
                    [
                        {type: 'special', text: '?123'},
                        {c: ','},
                        {type: 'space', text: '◀ Global ▶'},
                        {c: '.'},
                        {type: 'enter', icon: '<i class="fa-solid fa-arrow-turn-down" style="transform: rotate(90deg);"></i>'}
                    ]
                ]
            };
        }

        for (let r = 1; r <= 4; r++) {
            const rowElem = document.getElementById(`kb-r${r}`);
            rowElem.innerHTML = '';
            const rowData = layout.rows[r - 1];

            rowData.forEach(item => {
                const key = document.createElement('div');
                key.className = 'kb-key';

                if (item.type === 'special') {
                    key.classList.add('special');
                    key.innerHTML = item.icon || item.text;
                } else if (item.type === 'space') {
                    key.classList.add('space-key');
                    key.innerHTML = item.text;
                } else if (item.type === 'enter') {
                    key.classList.add('enter-key');
                    key.innerHTML = item.icon;
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
            if (!targetKey && ch === ' ') {
                targetKey = document.querySelector('.kb-key.space-key');
            }
            if (!targetKey) {
                const normalKeys = document.querySelectorAll('.kb-key[data-char]');
                if (normalKeys.length > 0) {
                    targetKey = normalKeys[Math.floor(Math.random() * normalKeys.length)];
                }
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

    function appendMessage(text, sender) {
        const div = document.createElement('div');
        div.className = sender === "1" ? "message-row me" : "message-row them";
        let html = '';
        if(sender === "2") html += `<img src="${chatData.pfp2}" class="them-pic">`;
        html += `<div class="bubble">${text}</div>`;
        div.innerHTML = html;
        document.getElementById('chat-area').insertBefore(div, document.getElementById('typing-row'));
        scrollToBottom();
    }

    // MAIN AUTO START: 3 SECONDS CLEAN PAUSE BEFORE CHAT STARTS
    async function startAutoChat() {
        // ১. ওভারলে সাথে সাথে হাইড হয়ে যাবে
        document.getElementById('overlay').style.display = 'none';

        // ২. ইউজারদের ভিডিও কাটার সুবিধার জন্য ৩ সেকেন্ড স্ক্রিন একদম স্থির থাকবে
        await sleep(3000);

        // ৩. ৩ সেকেন্ড পর মেসেজ ও কিবোর্ড টাইপিং শুরু হবে
        for (let msg of chatData.messages) {
            if (msg.sender === "1") {
                await simulateTypingKeyboard(msg.text); 
                appendMessage(msg.text, "1");
            } else {
                document.getElementById('typing-row').style.display = 'flex'; 
                scrollToBottom();
                await sleep(msg.text.length * 60 + 1000); 
                document.getElementById('typing-row').style.display = 'none'; 
                appendMessage(msg.text, "2");
            }
            document.getElementById('seen-pfp').style.display = 'none'; 
            await sleep(1000);
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
            <div class="mb-4"><label class="block font-bold mb-1">Chat Header Name</label><input type="text" id="chatName" class="w-full border p-2 rounded" required></div>
            <div class="mb-4">
                <h3 class="font-bold text-lg mb-2 border-b pb-1">Messages (Support Emoji/Any 194 Country Lang)</h3>
                <div id="messages-container"></div>
                <button type="button" onclick="addMsgRow()" class="mt-3 bg-blue-100 text-blue-700 px-3 py-1 rounded shadow">+ Add Message</button>
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-3 rounded-lg font-bold text-lg hover:bg-blue-700">Save Setup</button>
        </form>
    </div>
<script>
    let container = document.getElementById('messages-container');
    function addMsgRow(sender="1", text="") {
        const div = document.createElement('div'); div.className = "flex gap-2 mb-2 items-center";
        div.innerHTML = `<select class="border p-2 rounded w-1/4 msg-sender"><option value="1" ${sender==="1"?"selected":""}>Me</option><option value="2" ${sender==="2"?"selected":""}>Them</option></select><input type="text" class="border p-2 rounded w-3/4 msg-text" value="${text}" placeholder="Type text or emojis..." required><button type="button" onclick="this.parentElement.remove()" class="bg-red-500 text-white px-3 py-2 rounded">X</button>`;
        container.appendChild(div);
    }
    fetch('/api/get_data').then(r=>r.json()).then(data => {
        document.getElementById('pfp1').value = data.pfp1 || ""; document.getElementById('pfp2').value = data.pfp2 || ""; document.getElementById('chatName').value = data.name || "Unknown";
        if(data.messages) data.messages.forEach(m => addMsgRow(m.sender, m.text)); else addMsgRow();
    });
    document.getElementById('chatForm').onsubmit = function(e) {
        e.preventDefault(); let msgs = [];
        document.querySelectorAll('#messages-container > div').forEach(row => { msgs.push({sender: row.querySelector('.msg-sender').value, text: row.querySelector('.msg-text').value}); });
        fetch('/api/save_data', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({pfp1: document.getElementById('pfp1').value, pfp2: document.getElementById('pfp2').value, name: document.getElementById('chatName').value, messages: msgs}) }).then(() => alert("Chat setup saved successfully!"));
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
