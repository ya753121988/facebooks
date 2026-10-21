<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Messenger Exact Clone with Temp Data</title>
    <!-- Font Awesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
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
            overflow: hidden;
        }

        /* Mobile Phone Container */
        .app-container {
            width: 100%;
            max-width: 400px;
            height: 100%;
            background-color: #F3F6F8;
            display: flex;
            flex-direction: column;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
            position: relative;
        }

        /* iOS Status Bar (Like the image 12:35) */
        .status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 20px 5px 20px;
            font-size: 13px;
            font-weight: 600;
            color: #000;
        }
        .notch {
            width: 120px;
            height: 20px;
            background-color: #000;
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            border-bottom-left-radius: 15px;
            border-bottom-right-radius: 15px;
        }
        .status-icons i {
            margin-left: 5px;
            font-size: 12px;
        }

        /* Header / App Bar */
        .header {
            display: flex;
            align-items: center;
            padding: 10px 15px;
            background-color: #F3F6F8;
        }
        
        .header-icon {
            color: #0084FF;
            font-size: 20px;
            cursor: pointer;
        }

        .profile-info {
            display: flex;
            align-items: center;
            flex: 1;
            margin-left: 15px;
        }

        /* Active Status Dot Setup */
        .avatar-container {
            position: relative;
            display: inline-block;
        }

        .avatar-container img {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            object-fit: cover;
        }

        .active-dot {
            position: absolute;
            bottom: 2px;
            right: 0px;
            width: 11px;
            height: 11px;
            background-color: #31A24C; /* Messenger Green Active Color */
            border: 2px solid #F3F6F8;
            border-radius: 50%;
        }

        .profile-info h3 {
            font-size: 16px;
            margin-left: 10px;
            color: #000;
        }

        .header-actions {
            display: flex;
            gap: 18px;
        }

        /* Chat Body */
        .chat-body {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            padding-bottom: 30px;
            display: flex;
            flex-direction: column;
            scroll-behavior: smooth;
        }
        
        /* Hide scrollbar for clean look */
        .chat-body::-webkit-scrollbar {
            display: none;
        }

        /* Top Profile Banner */
        .top-profile {
            text-align: center;
            margin-bottom: 25px;
            margin-top: 10px;
        }

        .top-profile img {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            object-fit: cover;
        }

        .top-profile h2 {
            font-size: 22px;
            margin-top: 10px;
            color: #000;
        }

        .top-profile p {
            font-size: 13px;
            color: #555;
            margin-top: 5px;
        }

        .btn-view-profile {
            background-color: #E4E6EB;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
            margin-top: 15px;
            cursor: pointer;
        }

        .security-notice {
            font-size: 11px;
            color: #65676B;
            margin-top: 15px;
            line-height: 1.4;
            padding: 0 15px;
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

        /* Message Bubbles */
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
            margin-bottom: 3px;
            align-items: flex-end;
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

        .message-bubble {
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 16px;
            max-width: 75%;
            word-wrap: break-word;
        }

        .me .message-bubble {
            background-color: #0084FF;
            color: white;
        }

        .other .message-bubble {
            background-color: #E4E6EB;
            color: black;
        }
        
        .spacer {
            width: 32px; /* Space for hidden avatar alignment */
        }

        /* Scroll Down Indicator (From the image) */
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
            color: #65676B;
            font-size: 14px;
            z-index: 10;
            cursor: pointer;
        }

        /* Bottom Input Bar */
        .input-bar {
            display: flex;
            align-items: center;
            padding: 10px 12px;
            background-color: #F3F6F8;
            padding-bottom: 20px; /* Safe area for modern phones */
        }

        .input-icon {
            color: #0084FF;
            font-size: 24px;
            margin-right: 12px;
            cursor: pointer;
        }

        .input-field-container {
            flex: 1;
            background-color: #E4E6EB;
            border-radius: 20px;
            display: flex;
            align-items: center;
            padding: 8px 15px;
            margin-right: 12px;
        }

        .input-field-container input {
            border: none;
            background: transparent;
            outline: none;
            flex: 1;
            font-size: 16px;
            color: #000;
        }

        .input-field-container input::placeholder {
            color: #65676B;
        }

        .emoji-icon {
            color: #0084FF;
            font-size: 20px;
            cursor: pointer;
        }
        
        /* Send button toggle */
        #sendBtn {
            transition: 0.2s;
        }
    </style>
</head>
<body>

    <div class="app-container">
        <!-- Fake iOS Status Bar -->
        <div class="notch"></div>
        <div class="status-bar">
            <span>12:35</span>
            <div class="status-icons">
                <i class="fa-solid fa-signal"></i>
                <i class="fa-solid fa-wifi"></i>
                <i class="fa-solid fa-battery-full"></i>
            </div>
        </div>

        <!-- Header -->
        <div class="header">
            <i class="fa-solid fa-chevron-left header-icon"></i>
            <div class="profile-info">
                <div class="avatar-container">
                    <img src="https://i.pravatar.cc/150?img=11" alt="Profile">
                    <!-- Active Green Dot -->
                    <div class="active-dot"></div> 
                </div>
                <h3>Reji Kabeer B</h3>
            </div>
            <div class="header-actions">
                <i class="fa-solid fa-phone header-icon"></i>
                <i class="fa-solid fa-video header-icon"></i>
            </div>
        </div>

        <!-- Scroll Down Arrow (Like in the image) -->
        <div class="scroll-down-btn" onclick="scrollToBottom()">
            <i class="fa-solid fa-arrow-down"></i>
        </div>

        <!-- Chat Area -->
        <div class="chat-body" id="chatBox">
            <!-- Profile Banner -->
            <div class="top-profile">
                <img src="https://i.pravatar.cc/150?img=11" alt="Profile Big">
                <h2>Reji Kabeer B</h2>
                <p>You're friends on Facebook</p>
                <button class="btn-view-profile">View profile</button>
                
                <p class="security-notice">
                    <i class="fa-solid fa-lock" style="font-size: 10px;"></i> Messages and calls are secured with end-to-end encryption. Only people in this chat can read, listen to, or share them. <span>Learn more</span>
                </p>
                
                <p class="friend-notice">You're now friends with Reji Kabeer.</p>
            </div>

            <!-- Messages will be injected here dynamically by JavaScript -->
            <div id="messageContainer"></div>
        </div>

        <!-- Input Bar -->
        <div class="input-bar">
            <i class="fa-solid fa-camera input-icon"></i>
            <i class="fa-solid fa-image input-icon"></i>
            <i class="fa-solid fa-microphone input-icon" id="micIcon"></i>
            
            <div class="input-field-container">
                <input type="text" id="chatInput" placeholder="Aa">
                <i class="fa-solid fa-face-smile emoji-icon"></i>
            </div>
            
            <i class="fa-solid fa-thumbs-up input-icon" id="sendBtn" style="margin-right: 0;"></i>
        </div>
    </div>

    <script>
        // Default Messages from your screenshot
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
        const sendBtn = document.getElementById('sendBtn');
        const micIcon = document.getElementById('micIcon');

        // Load Temp Data (Local Storage)
        function loadMessages() {
            let savedData = localStorage.getItem('chatTempData');
            let messages = savedData ? JSON.parse(savedData) : defaultMessages;
            
            messageContainer.innerHTML = ''; // Clear box
            
            messages.forEach(msg => {
                appendMessageToUI(msg);
            });
            scrollToBottom();
        }

        // Render HTML for messages
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

        // Save new message permanently (so it doesn't wipe on reload)
        function saveMessage(text, type) {
            let savedData = localStorage.getItem('chatTempData');
            let messages = savedData ? JSON.parse(savedData) : defaultMessages;
            
            messages.push({ type: type, text: text });
            localStorage.setItem('chatTempData', JSON.stringify(messages)); // Saves to browser temp data
            
            appendMessageToUI({ type: type, text: text });
            scrollToBottom();
        }

        // Handle Send action
        function handleSend() {
            let text = chatInput.value.trim();
            if (text !== '') {
                saveMessage(text, 'me'); // Saves as "me" (Admin/User)
                chatInput.value = '';
                toggleSendIcon();
            }
        }

        // Change Thumbs Up to Send Arrow when typing
        function toggleSendIcon() {
            if (chatInput.value.trim().length > 0) {
                sendBtn.className = "fa-solid fa-paper-plane input-icon";
                micIcon.style.display = "none"; // Hide mic like real messenger
            } else {
                sendBtn.className = "fa-solid fa-thumbs-up input-icon";
                micIcon.style.display = "block";
            }
        }

        // Event Listeners
        sendBtn.addEventListener('click', handleSend);
        
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') handleSend();
        });

        chatInput.addEventListener('input', toggleSendIcon);

        function scrollToBottom() {
            setTimeout(() => {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 100);
        }

        // Initialize Chat on load
        window.onload = loadMessages;
    </script>

</body>
</html>
