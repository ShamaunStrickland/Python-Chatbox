import subprocess
import re
import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='AnadrosSite', static_folder='static')
socketio = SocketIO(app)

# Function to start the chatbot process
chatbox_process = None


def start_chatbot():
    global chatbox_process
    # Run chatbox script
    chatbox_script_path = 'chatbox.py'
    print("Running chatbot script:", chatbox_script_path)
    chatbox_process = subprocess.Popen(['python3', chatbox_script_path], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)


# Remove ANSI escape codes from the input text
def remove_ansi_escape_codes(text):
    # Remove ANSI escape codes and the specific sequence
    return re.sub(r'(\x1b\[[0-9;]*m)|(\x1B\[[0-9;]*[HJ])', '', text)


# Route for homepage
@app.route('/')
def index():
    # Print current working directory
    print("Current working directory:", os.getcwd())

    # List files in current directory
    print("Files in current directory:", os.listdir())

    # Run the training script
    training_script_path = 'training.py'
    print("Running training script:", training_script_path)
    subprocess.run(['python3', training_script_path])

    # Start chatbot after training finishes
    start_chatbot()

    return render_template('index.html')


# Event handler for receiving messages from the frontend
@socketio.on('send_message')
def handle_message(data):
    user_input = data['message']

    # Send user input to chatbox script
    chatbox_process.stdin.write(user_input.encode('utf-8') + b'\n')
    chatbox_process.stdin.flush()

    # Read the response from chatbox script
    bot_response = chatbox_process.stdout.readline().decode('utf-8').strip()

    # Remove ANSI escape codes from the bot response
    clean_response = remove_ansi_escape_codes(bot_response)

    # Check if the clean response is empty or contains unexpected characters
    if not clean_response:
        emit('bot_response', {'bot_response': 'Error: Empty response from bot'})
    elif not clean_response.startswith('Error:'):
        # If clean response doesn't start with 'Error:', emit it as a bot response
        emit('bot_response', {'bot_response': clean_response})
    else:
        # If clean response starts with 'Error:', emit it as an error
        emit('bot_response', {'bot_response': clean_response})


if __name__ == '__main__':
    # Start the Flask application
    socketio.run(app, debug=True)
