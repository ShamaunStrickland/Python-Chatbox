document.addEventListener('DOMContentLoaded', function () {
    // Connect to the Flask-SocketIO server
    var socket = io();  // Automatically tries to connect to the server that serves the page

    // Function to display user message in the chat box
    function displayUserMessage(userInput) {
        var messageDiv = document.createElement('div');
        messageDiv.className = 'user-message';
        messageDiv.textContent = 'User: ' + userInput.trim();
        document.getElementById('chat-box').appendChild(messageDiv);
        document.getElementById('user-input').value = '';
    }

    // Function to display bot response in the chat box
    function displayBotResponse(botResponse) {
        botResponse = botResponse.replace(/[^\x20-\x7E]/g, ''); // Clean non-printable characters
        var messageDiv = document.createElement('div');
        messageDiv.className = 'bot-message';
        messageDiv.textContent = 'Bot: ' + botResponse.trim();
        document.getElementById('chat-box').appendChild(messageDiv);
    }

    // Function to send user message to Flask server via Socket.IO
    function sendMessage() {
        var userInput = document.getElementById('user-input').value;
        displayUserMessage(userInput);
        socket.emit('chat_message', userInput); // Emitting a message to the server
    }

    // Event listener for send button click
    document.getElementById('send-btn').addEventListener('click', function () {
        document.getElementById('loader').style.display = 'inline-block';
        sendMessage();
    });

    // Event listener for Enter key press in input field
    document.getElementById('user-input').addEventListener('keypress', function (event) {
        if (event.keyCode === 13) {
            document.getElementById('loader').style.display = 'inline-block';
            sendMessage();
        }
    });

    // Event handler for receiving bot response from the server via Socket.IO
    socket.on('bot_response', function (data) {
        document.getElementById('loader').style.display = 'none';
        console.log('Received data from server:', data);
        displayBotResponse(data);
    });
});
