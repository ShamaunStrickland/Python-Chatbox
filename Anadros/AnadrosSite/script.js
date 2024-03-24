// Function to display user message in the chat box
function displayUserMessage(userInput) {
    // Display user message in the chat box
    document.getElementById('chat-box').innerHTML += '<div class="user-message">' + userInput + '</div>';
    // Clear input field
    document.getElementById('user-input').value = '';
}

// Function to display bot response in the chat box
function displayBotResponse(botResponse) {
    // Add bot response to the chat box
    document.getElementById('chat-box').innerHTML += '<div class="bot-message">' + botResponse + '</div>';
}

// Function to send user message
function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    // Display user message in the chat box
    displayUserMessage(userInput);
}

// Event listener for send button click
document.getElementById('send-btn').addEventListener('click', function () {
    sendMessage();
});

// Event listener for Enter key press in input field
document.getElementById('user-input').addEventListener('keypress', function (event) {
    if (event.keyCode === 13) {
        sendMessage();
    }
});
