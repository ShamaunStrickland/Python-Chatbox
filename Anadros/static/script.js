// Connect to the Flask server using Websockets
var socket = io.connect('http://' + document.domain + ':' + location.port);

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
    socket.emit('send_message', {message: userInput});
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
socket.on('bot_response', function (data) {
    // Log the received data for debugging
    console.log('Received data from server:', data);
    // Display bot response in the chat box
    displayBotResponse(data.bot_response);
    // Hide loader icon and show send button
    document.getElementById('loader').style.display = 'none';
    document.getElementById('send-btn').style.display = 'block';
});
