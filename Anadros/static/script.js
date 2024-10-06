import {io} from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js";

const socket = io('http://anadros.com', {  // Changed 'wss' to 'http'
    transports: ['websocket'],
    reconnectionAttempts: 5,
});

// Connection success handler
socket.on('connect', () => {
    console.log('Successfully connected to the server.');
});

// Error handling for connection issues
socket.on('connect_error', (error) => {
    console.error('Connection Error:', error);
});

// Event listener for 'bot_response' event
socket.on('bot_response', (data) => {
    console.log('Received response:', data);
    displayBotResponse(data);
});

// Handle disconnection
socket.on('disconnect', (reason) => {
    console.log('Disconnected:', reason);
});

function displayBotResponse(response) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'bot-message';
    messageDiv.textContent = 'Bot: ' + response;
    chatBox.appendChild(messageDiv);
}

document.getElementById('send-btn').addEventListener('click', () => {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim()) {
        displayUserMessage(userInput);
        sendMessage(userInput);
        document.getElementById('user-input').value = ''; // Clear the input after sending
    }
});

function displayUserMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'user-message';
    messageDiv.textContent = 'User: ' + message;
    chatBox.appendChild(messageDiv);
}

function sendMessage(message) {
    // This check ensures that we only try to send messages when the socket is connected
    if (socket.connected) {
        socket.emit('chat_message', message);
    } else {
        console.log('Socket is not connected.');
    }
}
