// JavaScript for chatbot functionality

// Function to send user message to chatbox
function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    document.getElementById('chat-box').innerHTML += '<div class="user-message">' + userInput + '</div>';
    document.getElementById('user-input').value = '';
    // Call function to handle bot response
    getBotResponse(userInput);
}

// Function to handle bot response
function getBotResponse(userInput) {
    // Add loader animation while waiting for response
    document.getElementById('loader').style.display = 'block';
    // Simulate response delay
    setTimeout(function () {
        // Dummy bot response (replace with actual response)
        var botResponse = 'This is a sample bot response to: ' + userInput;
        document.getElementById('chat-box').innerHTML += '<div class="bot-message">' + botResponse + '</div>';
        // Hide loader animation after response
        document.getElementById('loader').style.display = 'none';
    }, 1000); // Simulate 1 second delay (replace with actual API call)
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
