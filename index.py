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
        {"sender": "1", "text": "হ্যালো মার্ক! কেমন আছো?"},
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

# ================= PWA SETUP (App Installer - 100% Working) ================= #

@app.route('/manifest.json')
def manifest():
    manifest_data = {
        "name": "Auto Chat Video",
        "short_name": "ChatVideo",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#0084ff",
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
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { margin: 0; font-family: 'Segoe UI', Helvetica, Arial, sans-serif; background-color: #000; display: flex; justify-content: center; height: 100vh; overflow: hidden; }
        .messenger-container { background: #fff; width: 100%; max-w-md: 400px; height: 100vh; display: flex; flex-direction: column; position: relative; max-width: 450px; }
        
        /* Header & Active Dot */
        .header { display: flex; align-items: center; justify-content: space-between; padding: 10px 15px; border-bottom: 1px solid #e0e0e0; z-index: 10; background: #fff;}
        .header-left { display: flex; align-items: center; gap: 12px; }
        .back-btn { color: #0084ff; font-size: 22px; cursor: pointer; }
        .pfp-container { position: relative; width: 38px; height: 38px; }
        .profile-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        .active-dot { position: absolute; bottom: 0; right: 0; width: 10px; height: 10px; background-color: #31a24c; border: 2px solid #fff; border-radius: 50%; }
        
        .user-info { display: flex; flex-direction: column; }
        .user-name { font-weight: 600; font-size: 16px; color: #050505; }
        .active-status { font-size: 12px; color: #65676B; }
        .header-icons i { color: #0084ff; font-size: 20px; margin-left: 18px; cursor: pointer;}

        /* Chat Area */
        .chat-area { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; background: #ffffff; padding-bottom: 20px;}
        .message-row { display: flex; margin-bottom: 15px; width: 100%; align-items: flex-end;}
        .message-row.me { justify-content: flex-end; }
        .message-row.them { justify-content: flex-start; }
        
        .them-pic { width: 28px; height: 28px; border-radius: 50%; margin-right: 8px; object-fit: cover;}
        .bubble { max-width: 70%; padding: 10px 14px; border-radius: 18px; font-size: 15px; word-wrap: break-word; line-height: 1.4; }
        .me .bubble { background: #0084ff; color: white; border-bottom-right-radius: 4px; }
        .them .bubble { background: #e4e6eb; color: black; border-bottom-left-radius: 4px; }
        
        /* 3 Dots Typing Indicator */
        .typing-bubble { background: #e4e6eb; padding: 12px 16px; border-radius: 18px; border-bottom-left-radius: 4px; display: flex; gap: 4px; align-items: center; width: fit-content; }
        .dot { width: 6px; height: 6px; background-color: #8D949E; border-radius: 50%; animation: typing 1.4s infinite ease-in-out both; }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes typing { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

        /* Input Area */
        .input-area { display: flex; align-items: center; padding: 10px; border-top: 1px solid #e0e0e0; background: #fff; z-index: 5;}
        .input-icons i { color: #0084ff; font-size: 22px; margin-right: 12px; }
        .input-box { flex: 1; background: #f0f2f5; border-radius: 20px; padding: 8px 15px; font-size: 15px; border: none; outline: none; }
        .input-right-icon { color: #0084ff; font-size: 22px; margin-left: 12px; transition: 0.2s;}

        /* Fake Keyboard Overlay */
        .keyboard-area { height: 0; background: #d1d4d9; transition: height 0.3s; overflow: hidden; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative;}
        .keyboard-area.active { height: 260px; }
        .kb-row { display: flex; gap: 6px; margin-bottom: 8px; justify-content: center; width: 100%; padding: 0 5px;}
        .kb-key { background: #fff; padding: 12px; border-radius: 6px; box-shadow: 0 1px 1px rgba(0,0,0,0.2); flex: 1; text-align: center; font-size: 18px; max-width: 35px; transition: background 0.1s;}
        .kb-key.pressed { background: #aeb3ba; transform: scale(0.95); }
        .kb-lang-hint { position: absolute; top: 5px; right: 10px; font-size: 10px; color: #555; font-weight: bold;}

        /* Overlays */
        .overlay-start { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); display: flex; justify-content: center; align-items: center; z-index: 100; flex-direction: column; color: white;}
        .start-btn { background: #0084ff; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 10px; cursor: pointer; margin-top: 20px; font-weight: bold;}
        .seen-indicator { width: 14px; height: 14px; border-radius: 50%; object-fit: cover; align-self: flex-end; margin-top: 4px; display: none; }
    </style>
</head>
<body>

<div class="messenger-container" id="messenger">
    <!-- Start Recording Overlay -->
    <div class="overlay-start" id="overlay">
        <h2>Ready to Record</h2>
        <p style="text-align:center; padding: 0 20px; font-size: 14px; color:#ddd; line-height: 1.5;">
            Click Start to play chat in Fullscreen!<br>
            <span style="font-size:12px; color:#aaa;">(মোবাইলে ভিডিও করতে ফোনের বিল্ট-ইন Screen Recorder অন করে Start চাপুন)</span>
        </p>
        <button class="start-btn" onclick="startAutoChat()">Start Chat</button>
    </div>

    <!-- Header -->
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

    <!-- Bottom Input -->
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

    <!-- Fake Animated Virtual Keyboard -->
    <div class="keyboard-area" id="keyboard">
        <div class="kb-lang-hint" id="kb-lang">EN</div>
        <div class="kb-row" id="kb-r1"></div>
        <div class="kb-row" id="kb-r2"></div>
        <div class="kb-row" id="kb-r3"></div>
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

    // Keyboard Logic
    const layouts = {
        'EN': ['qwertyuiop', 'asdfghjkl', 'zxcvbnm'],
        'BN': ['কখগঘঙচছজঝঞ', 'টঠডঢণতথদধন', 'পফবভমযরলশষ'],
        'HI': ['कखगघङचछजझञ', 'टठডढणतथदधन', 'पफबभमयरलवश'],
        'EM': ['😀😂🥰😎🤔', '😭🙏👍🔥💯', '❤️💔🎉🌟✅']
    };

    function setKeyboardLayout(text) {
        let lang = 'EN';
        const charCode = text.charCodeAt(0);
        if (charCode >= 0x0980 && charCode <= 0x09FF) lang = 'BN'; 
        else if (charCode >= 0x0900 && charCode <= 0x097F) lang = 'HI'; 
        else if (charCode > 255) lang = 'EM'; 

        document.getElementById('kb-lang').innerText = lang;
        const layout = layouts[lang] || layouts['EN'];

        for(let i=1; i<=3; i++) {
            let rowHtml = '';
            for(let char of layout[i-1]) {
                rowHtml += `<div class="kb-key" id="key-${char}">${char}</div>`;
            }
            document.getElementById(`kb-r${i}`).innerHTML = rowHtml;
        }
    }

    async function simulateTypingKeyboard(text) {
        const kb = document.getElementById('keyboard');
        kb.classList.add('active'); 
        setKeyboardLayout(text);
        await sleep(500);

        const input = document.getElementById('msg-input');
        const icon = document.getElementById('send-icon');
        icon.classList.remove('fa-thumbs-up'); icon.classList.add('fa-paper-plane');
        
        for (let i = 0; i < text.length; i++) {
            input.value += text[i];
            const keys = document.querySelectorAll('.kb-key');
            if(keys.length > 0) {
                const randomKey = keys[Math.floor(Math.random() * keys.length)];
                randomKey.classList.add('pressed');
                setTimeout(() => randomKey.classList.remove('pressed'), 100);
            }
            await sleep(150); 
        }
        await sleep(400); 
        input.value = "";
        icon.classList.remove('fa-paper-plane'); icon.classList.add('fa-thumbs-up');
        kb.classList.remove('active'); 
        await sleep(300);
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

    // MAIN AUTO RECORD FUNCTION WITH FULLSCREEN (ERROR-FREE & MOBILE/PC COMPATIBLE)
    async function startAutoChat() {
        let mediaRecorder = null;
        let stream = null;

        // ১. অটোমেটিক ফুল-স্ক্রিন করা
        try {
            if (document.documentElement.requestFullscreen) {
                await document.documentElement.requestFullscreen();
            } else if (document.documentElement.webkitRequestFullscreen) {
                await document.documentElement.webkitRequestFullscreen();
            } else if (document.documentElement.msRequestFullscreen) {
                await document.documentElement.msRequestFullscreen();
            }
        } catch (e) {
            console.log("Fullscreen request was prevented or not supported.");
        }

        // ২. ব্রাউজার স্ক্রিন রেকর্ডিং ট্রাই করা (শুধুমাত্র পিসিতে কাজ করবে, মোবাইলে ক্র্যাশ করবে না)
        if (navigator.mediaDevices && typeof navigator.mediaDevices.getDisplayMedia === 'function') {
            try {
                stream = await navigator.mediaDevices.getDisplayMedia({
                    video: { displaySurface: "browser" }, 
                    audio: false
                });

                if (window.MediaRecorder) {
                    let options = { mimeType: 'video/webm' };
                    if (!MediaRecorder.isTypeSupported('video/webm')) {
                        options = MediaRecorder.isTypeSupported('video/mp4') ? { mimeType: 'video/mp4' } : {};
                    }
                    mediaRecorder = new MediaRecorder(stream, options);
                    const chunks = [];
                    mediaRecorder.ondataavailable = (e) => {
                        if (e.data && e.data.size > 0) chunks.push(e.data);
                    };
                    mediaRecorder.onstop = () => {
                        const blob = new Blob(chunks, { type: mediaRecorder.mimeType || 'video/webm' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url; 
                        a.download = 'messenger_chat_video.webm'; 
                        a.click();
                    };
                    mediaRecorder.start();
                }
            } catch (err) {
                console.log("Screen recording not started or permission cancelled on this device.");
            }
        }

        // ৩. ওভারলে বন্ধ করে চ্যাট অ্যানিমেশন শুরু করা
        document.getElementById('overlay').style.display = 'none';
        await sleep(1000);

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

        // ৪. চার সেকেন্ড পর ভিডিও অটো সেভ এবং ফুলস্ক্রিন এক্সিট
        await sleep(4000); 
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        try {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        } catch(e) {}
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
                <h3 class="font-bold text-lg mb-2 border-b pb-1">Messages (Support Emoji/Any Lang)</h3>
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
