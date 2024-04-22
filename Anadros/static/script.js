// Determine the protocol (HTTP or HTTPS) based on the current page URL
var protocol = location.protocol === 'https:' ? 'wss://' : 'ws://';

// Construct the WebSocket URL
var socketUrl = protocol + document.domain + ':' + location.port + '/websocket';

// Connect to the Flask server using Websockets with the determined protocol
var socket = new WebSocket(socketUrl);

// Error handler for WebSocket connection
socket.onerror = function (error) {
    console.error('WebSocket connection error:', error.message);
    // Handle the error, such as displaying an error message to the user
    // You can also attempt to reconnect here if appropriate
};

// Function to display user message in the chat box
function displayUserMessage(userInput) {
    // Create a new div element for the user message
    var messageDiv = document.createElement('div');
    messageDiv.className = 'user-message';
    // Set the inner text of the div to the user input
    messageDiv.innerText = 'User: ' + userInput.trim(); // Trim any leading or trailing whitespace
    // Append the message div to the chat box
    document.getElementById('chat-box').appendChild(messageDiv);
    // Clear input field
    document.getElementById('user-input').value = '';
}

// Function to display bot response in the chat box
function displayBotResponse(botResponse) {
    // Clean the bot response by removing any non-printable characters
    botResponse = botResponse.replace(/[^\x20-\x7E]/g, ''); // Remove non-printable characters
    // Create a new div element for the bot response
    var messageDiv = document.createElement('div');
    messageDiv.className = 'bot-message';
    // Set the inner text of the div to the cleaned bot response
    messageDiv.innerText = 'Bot: ' + botResponse.trim(); // Trim any leading or trailing whitespace
    // Append the message div to the chat box
    document.getElementById('chat-box').appendChild(messageDiv);
}

// Function to send user message to Flask server via Websockets
function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    // Display user message in the chat box
    displayUserMessage(userInput);
    // Show loader icon and hide send button
    document.getElementById('loader').style.display = 'block';
    document.getElementById('send-btn').style.display = 'none';
    // Send user message to Flask server via Websockets
    socket.send(JSON.stringify({message: userInput}));
}

// Event listener for send button click
document.getElementById('send-btn').addEventListener('click', sendMessage);

// Event listener for Enter key press in input field
document.getElementById('user-input').addEventListener('keypress', function (event) {
    if (event.keyCode === 13) {
        sendMessage();
    }
});

// Event handler for receiving bot response from the server via Websockets
socket.onmessage = function (event) {
    // Log the received data for debugging
    console.log('Received data from server:', event.data);
    // Display bot response in the chat box
    displayBotResponse(JSON.parse(event.data).bot_response);
    // Hide loader icon and show send button
    document.getElementById('loader').style.display = 'none';
    document.getElementById('send-btn').style.display = 'block';
};

// Keep-alive mechanism: Send a message to the server every 15 seconds to keep the connection alive
setInterval(function () {
    socket.send(JSON.stringify({keep_alive: true}));
}, 15000); // Send a keep-alive message every 15 seconds
