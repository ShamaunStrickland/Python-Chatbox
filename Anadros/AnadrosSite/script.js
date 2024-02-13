// Function to send user message to Flask server
function sendMessageToServer(userInput) {
    fetch('/chat?message=' + encodeURIComponent(userInput))
    .then(response => response.text())
    .then(botResponse => {
        // Add bot response to the chat box
        document.getElementById('chat-box').innerHTML += '<div class="bot-message">' + botResponse + '</div>';
        // Hide loader animation after response
        document.getElementById('loader').style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        // Hide loader animation in case of error
        document.getElementById('loader').style.display = 'none';
    });
}

// Function to send user message and receive bot response
function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    // Display user message in the chat box
    document.getElementById('chat-box').innerHTML += '<div class="user-message">' + userInput + '</div>';
    // Clear input field
    document.getElementById('user-input').value = '';
    // Show loader animation
    document.getElementById('loader').style.display = 'block';
    // Send user message to Flask server and get bot response
    sendMessageToServer(userInput);
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
