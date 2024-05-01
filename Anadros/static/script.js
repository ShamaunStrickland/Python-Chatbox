// Import the Socket.IO client library
import {io} from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js";

// Connect to the server
const socket = io();

// Event listener for the 'connect' event
socket.on('connect', () => {
    console.log('Connected to the server.');
});

// Event listener for receiving bot responses
socket.on('bot_response', (data) => {
    displayBotResponse(data);
});

// Event listener for the 'disconnect' event
socket.on('disconnect', () => {
    console.log('Disconnected from the server.');
});

// Function to display bot responses in the chat box
function displayBotResponse(response) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = 'Bot: ' + response;
    messageDiv.className = 'bot-message';
    document.getElementById('chat-box').appendChild(messageDiv);
}

// Function to send a message to the server
function sendMessage(message) {
    socket.emit('chat_message', message);
}

// Add event listener to the send button
document.getElementById('send-btn').addEventListener('click', () => {
    const userInput = document.getElementById('user-input').value.trim();
    if (userInput) {
        displayUserMessage(userInput);
        sendMessage(userInput);
        document.getElementById('user-input').value = ''; // Clear the input field after sending
    }
});

// Function to display user messages in the chat box
function displayUserMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = 'User: ' + message;
    messageDiv.className = 'user-message';
    document.getElementById('chat-box').appendChild(messageDiv);
}

// Add event listener for the 'Enter' key in the input field
document.getElementById('user-input').addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        const userInput = document.getElementById('user-input').value.trim();
        if (userInput) {
            displayUserMessage(userInput);
            sendMessage(userInput);
            document.getElementById('user-input').value = ''; // Clear the input field after sending
        }
    }
});
