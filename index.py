<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Messenger Exact Clone - Reji Kabeer B</title>
    
    <style>
        /* Global Reset */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        body {
            background-color: #d9d9d9;
            display: flex;
            justify-content: center;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }

        /* App Container (Mobile Size) */
        .app-container {
            width: 100%;
            max-width: 400px;
            height: 100%;
            background-color: #EBF0F6; /* Slight bluish-gray tint matching the image */
            display: flex;
            flex-direction: column;
            position: relative;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }

        /* Header */
        .header {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            background-color: #EBF0F6;
            z-index: 10;
        }

        .icon-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .icon-btn svg {
            fill: #0084FF;
            width: 24px;
            height: 24px;
        }

        .profile-info {
            display: flex;
            align-items: center;
            flex: 1;
            margin-left: 10px;
        }
        .profile-info img {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            object-fit: cover;
        }
        .profile-info h3 {
            font-size: 16px;
            margin-left: 10px;
            color: #000;
            font-weight: 600;
        }

        .header-actions {
            display: flex;
            gap: 15px;
        }

        /* Chat Body */
        .chat-body {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            scroll-behavior: smooth;
            padding-bottom: 20px;
        }
        .chat-body::-webkit-scrollbar {
            display: none;
        }

        /* Top Profile Banner */
        .top-profile {
            text-align: center;
            margin-bottom: 25px;
            margin-top: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .top-profile img {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            object-fit: cover;
        }
        .top-profile h2 {
            font-size: 20px;
            margin-top: 10px;
            color: #000;
        }
        .top-profile p {
            font-size: 13px;
            color: #555;
            margin-top: 2px;
        }
        .btn-view-profile {
            background-color: rgba(0,0,0,0.05);
            border: none;
            padding: 7px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            margin-top: 12px;
            cursor: pointer;
        }

        .security-notice {
            font-size: 11px;
            color: #65676B;
            margin-top: 15px;
            line-height: 1.4;
            padding: 0 15px;
            text-align: center;
        }
        .security-notice svg {
            width: 10px;
            height: 10px;
            fill: #65676B;
            margin-right: 2px;
            vertical-align: middle;
        }
        .security-notice span {
            color: #0084FF;
            font-weight: 600;
        }

        .friend-notice {
            font-size: 12px;
            color: #65676B;
            margin-top: 15px;
        }

        /* Messages */
        .timestamp {
            text-align: center;
            font-size: 11px;
            color: #65676B;
            font-weight: 500;
            margin: 20px 0 10px 0;
            text-transform: uppercase;
        }
        .message-row {
            display: flex;
            margin-bottom: 2px;
            align-items: flex-end;
            width: 100%;
        }
        .message-row.me {
            justify-content: flex-end;
        }
        .message-row.other {
            justify-content: flex-start;
        }
        .other-avatar {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            margin-right: 8px;
            object-fit: cover;
        }
        .spacer {
            width: 32px;
        }
        .message-bubble {
            padding: 9px 15px;
            border-radius: 18px;
            font-size: 16px;
            max-width: 75%;
            word-wrap: break-word;
        }
        .me .message-bubble {
            background-color: #0084FF;
            color: white;
        }
        .other .message-bubble {
            background-color: rgba(0,0,0,0.05);
            color: black;
        }

        /* Floating Scroll Down Arrow */
        .scroll-down-btn {
            position: absolute;
            bottom: 75px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 30px;
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
            cursor: pointer;
            z-index: 10;
        }
        .scroll-down-btn svg {
            width: 16px;
            height: 16px;
            fill: #65676B;
        }

        /* Bottom Input Bar */
        .bottom-bar {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            background-color: #EBF0F6;
            padding-bottom: 20px; /* Safe area */
        }
        .left-actions {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-right: 12px;
        }
        .left-actions svg {
            fill: #0084FF;
            width: 26px;
            height: 26px;
        }

        /* Input Box */
        .input-container {
            flex-grow: 1;
            background-color: rgba(0,0,0,0.05);
            border-radius: 20px;
            padding: 8px 15px;
            display: flex;
            align-items: center;
        }
        .input-container input {
            border: none;
            background: transparent;
            outline: none;
            width: 100%;
            font-size: 16px;
            color: #050505;
        }
        .input-container input::placeholder {
            color: #65676B;
        }
        .emoji-btn svg {
            fill: #0084FF;
            width: 22px;
            height: 22px;
            margin-left: 5px;
        }

        /* Send/Thumb Button */
        .action-btn {
            margin-left: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: transparent;
            border: none;
            cursor: pointer;
        }
        .action-btn svg {
            fill: #0084FF;
            width: 26px;
            height: 26px;
        }
        
        #sendIcon { display: none; } /* Hidden by default */
        #micIcon { display: block; }
    </style>
</head>
<body>

    <div class="app-container">
        
        <!-- Header (Reji Kabeer B) - ফেক স্ট্যাটাস বার রিমুভ করা হয়েছে -->
        <div class="header">
            <button class="icon-btn" style="margin-right: 5px;">
                <svg viewBox="0 0 24 24"><path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/></svg>
            </button>
            <div class="profile-info">
                <img src="https://i.pravatar.cc/150?img=11" alt="Profile">
                <h3>Reji Kabeer B</h3>
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

        <!-- Scroll Down Arrow Button -->
        <div class="scroll-down-btn" onclick="scrollToBottom()">
            <svg viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>
        </div>

        <!-- Chat Area -->
        <div class="chat-body" id="chatBox">
            <div class="top-profile">
                <img src="https://i.pravatar.cc/150?img=11" alt="Profile Big">
                <h2>Reji Kabeer B</h2>
                <p>You're friends on Facebook</p>
                <button class="btn-view-profile">View profile</button>
                <p class="security-notice">
                    <svg viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zM9 6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9V6zm9 14H6V10h12v10zm-6-3c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/></svg>
                    Messages and calls are secured with end-to-end encryption. Only people in this chat can read, listen to, or share them. <span>Learn more</span>
                </p>
                <p class="friend-notice">You're now friends with Reji Kabeer.</p>
            </div>

            <!-- Message Container for JS -->
            <div id="messageContainer"></div>
        </div>

        <!-- Bottom Input Bar -->
        <div class="bottom-bar">
            <div class="left-actions">
                <button class="icon-btn">
                    <!-- Camera SVG -->
                    <svg viewBox="0 0 24 24"><path d="M4 4h3l2-2h6l2 2h3c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2zm8 3c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 8c-1.65 0-3-1.35-3-3s1.35-3 3-3 3 1.35 3 3-1.35 3-3 3z"/></svg>
                </button>
                <button class="icon-btn">
                    <!-- Gallery SVG -->
                    <svg viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
                </button>
                <button class="icon-btn" id="micBtn">
                    <!-- Mic SVG -->
                    <svg id="micIcon" viewBox="0 0 24 24"><path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z"/></svg>
                </button>
            </div>
            
            <div class="input-container">
                <input type="text" id="chatInput" placeholder="Aa">
                <!-- Emoji SVG inside input -->
                <button class="icon-btn emoji-btn">
                    <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 8c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zm-7 0c.83 0 1.5.67 1.5 1.5S9.33 13 8.5 13 7 12.33 7 11.5 7.67 10 8.5 10zm3.5 8c-2.33 0-4.31-1.46-5.11-3.5h10.22c-.8 2.04-2.78 3.5-5.11 3.5z"/></svg>
                </button>
            </div>
            
            <button class="action-btn" id="sendOrThumbBtn">
                <!-- Thumb SVG -->
                <svg id="thumbIcon" viewBox="0 0 24 24"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
                <!-- Send Paper Plane SVG (Hidden initially) -->
                <svg id="sendIcon" viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
        </div>
    </div>

    <!-- JavaScript For Saving Data & Logic -->
    <script>
        // আপনার ছবির হুবহু মেসেজগুলো 
        const defaultMessages = [
            { type: 'time', text: 'SEP 3 AT 11:24 PM' },
            { type: 'me', text: 'Hey 👋' },
            { type: 'time', text: 'SEP 7 AT 6:34 PM' },
            { type: 'me', text: 'Hi' },
            { type: 'time', text: 'SEP 8 AT 1:40 PM' },
            { type: 'other', text: 'Hi', showAvatar: true },
            { type: 'time', text: 'SEP 8 AT 7:35 PM' },
            { type: 'me', text: 'Hi' }
        ];

        const messageContainer = document.getElementById('messageContainer');
        const chatBox = document.getElementById('chatBox');
        const chatInput = document.getElementById('chatInput');
        const sendOrThumbBtn = document.getElementById('sendOrThumbBtn');
        const thumbIcon = document.getElementById('thumbIcon');
        const sendIcon = document.getElementById('sendIcon');
        const micIcon = document.getElementById('micIcon');
        const micBtn = document.getElementById('micBtn');

        // Local Storage থেকে মেসেজ লোড করা
        function loadMessages() {
            let savedData = localStorage.getItem('rejiKabeerChatData');
            let messages = savedData ? JSON.parse(savedData) : defaultMessages;
            
            messageContainer.innerHTML = '';
            
            messages.forEach(msg => {
                appendMessageToUI(msg);
            });
            scrollToBottom();
        }

        // মেসেজ বক্সে শো করানো
        function appendMessageToUI(msg) {
            let div = document.createElement('div');
            
            if (msg.type === 'time') {
                div.className = 'timestamp';
                div.innerText = msg.text;
            } else if (msg.type === 'me') {
                div.className = 'message-row me';
                div.innerHTML = `<div class="message-bubble">${msg.text}</div>`;
            } else if (msg.type === 'other') {
                div.className = 'message-row other';
                let avatarHTML = msg.showAvatar ? `<img src="https://i.pravatar.cc/150?img=11" class="other-avatar">` : `<div class="spacer"></div>`;
                div.innerHTML = `${avatarHTML}<div class="message-bubble">${msg.text}</div>`;
            }
            messageContainer.appendChild(div);
        }

        // নতুন মেসেজ সেভ করা (যাতে রিফ্রেশ দিলে না মুছে যায়)
        function saveMessage(text, type) {
            let savedData = localStorage.getItem('rejiKabeerChatData');
            let messages = savedData ? JSON.parse(savedData) : defaultMessages;
            
            messages.push({ type: type, text: text });
            localStorage.setItem('rejiKabeerChatData', JSON.stringify(messages)); 
            
            appendMessageToUI({ type: type, text: text });
            scrollToBottom();
        }

        // সেন্ড বাটন ক্লিক ইভেন্ট
        function handleSend() {
            let text = chatInput.value.trim();
            if (text !== '') {
                saveMessage(text, 'me'); 
                chatInput.value = '';
                toggleIcons();
            } else {
                // If it's empty, it acts as a thumbs up button like Messenger
                saveMessage('👍', 'me');
                scrollToBottom();
            }
        }

        // টাইপ করার সময় Thumbs Up আইকন Send আইকনে বদলানো
        function toggleIcons() {
            if (chatInput.value.trim().length > 0) {
                thumbIcon.style.display = "none";
                sendIcon.style.display = "block";
                micBtn.style.display = "none"; // Hide Mic when typing
            } else {
                thumbIcon.style.display = "block";
                sendIcon.style.display = "none";
                micBtn.style.display = "flex"; // Show Mic when empty
            }
        }

        // ইভেন্ট লিসেনার
        sendOrThumbBtn.addEventListener('click', handleSend);
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') handleSend();
        });
        chatInput.addEventListener('input', toggleIcons);

        // নিজে নিজে নিচে স্ক্রল হওয়া
        function scrollToBottom() {
            setTimeout(() => {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 100);
        }

        // পেজ লোড হলেই রান হবে
        window.onload = loadMessages;
    </script>

</body>
</html>
