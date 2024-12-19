from gevent import monkey

# Patch all to make standard library cooperative
monkey.patch_all()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
import sys
import subprocess
import json
import requests
import time
import os
import threading
import queue
import redis
from flask_session import Session
from datetime import datetime

# Set up logging to write to stdout and stderr
logging.basicConfig(level=logging.DEBUG)
sys.stdout = sys.stderr  # Redirect stdout to stderr for consistent logging

# Set environment variable TF_USE_LEGACY_KERAS
os.environ["TF_USE_LEGACY_KERAS"] = "True"

app = Flask(__name__, template_folder='AnadrosSite', static_folder='static')

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Set up Redis for Flask-Session and SocketIO message queue
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'myapp_'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')

# Initialize session management
Session(app)

# Initialize Flask-SocketIO with Redis message queue
socketio = SocketIO(app, message_queue='redis://127.0.0.1:6379', async_mode='gevent')

# Global variable to store the chatbot process and queue
chatbot_process = None
stdout_queue = queue.Queue()
last_activity_time = time.time()


def start_chatbox():
    global chatbot_process
    dir_path = os.path.dirname(os.path.realpath(__file__))
    chatbox_script_path = os.path.join(dir_path, 'chatbox.py')
    try:
        chatbot_process = subprocess.Popen(
            ['python3', chatbox_script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            text=True  # Use text=True to read stdout as text
        )
        print("Chatbox process started successfully.")

        # Create a thread to read chatbot's stdout and put lines into the queue
        threading.Thread(target=read_stdout, args=(chatbot_process.stdout,), daemon=True).start()

        return True
    except Exception as e:
        print(f"Error starting chatbox process: {e}")
        return False


def read_stdout(stdout):
    """Read stdout line by line and put it in a queue."""
    try:
        for line in iter(stdout.readline, ''):  # Read line by line
            print(f"Line from chatbot: {line.strip()}")
            stdout_queue.put(line.strip())
    except Exception as e:
        print(f"Error reading stdout: {e}")


def non_blocking_read():
    """Return one line from the queue if available, else return None."""
    try:
        return stdout_queue.get(timeout=5)  # Wait for 5 seconds for response
    except queue.Empty:
        print("No response from chatbot within timeout.")
        return None


def get_location(ip_address):
    url = f'http://ip-api.com/json/{ip_address}?fields=status,message,city,regionName,country,lat,lon'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                location = {
                    'city': data['city'],
                    'region': data['regionName'],  # State or Region
                    'country': data['country'],
                    'latitude': data['lat'],
                    'longitude': data['lon']
                }
                return json.dumps(location)
        return 'Unknown'
    except Exception as e:
        print(f"Error getting location: {e}")
        return 'Unknown'


def log_request(ip_address, message):
    location = get_location(ip_address)
    browser_info = request.user_agent.string
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_data = {
        'IP Address': ip_address,
        'Location': location,
        'Message': message,
        'Browser Info': browser_info,
        'Date/Time': current_time
    }

    with open('request_logs.txt', 'a') as log_file:
        log_file.write(f'{json.dumps(log_data)}\n\n')

    print(f"IP Address: {ip_address}, Location: {location}, Message: {message}, "
          f"Browser Info: {browser_info}, Time: {current_time}")


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    global last_activity_time
    last_activity_time = time.time()
    print("Client connected.")


@socketio.on('chat_message')
def handle_message(data):
    ip_address = request.remote_addr
    log_request(ip_address, data)

    if chatbot_process and chatbot_process.poll() is None:
        try:
            print("Sending data to chatbot:", data)
            chatbot_process.stdin.write(data + '\n')  # Send plain string, no encoding
            chatbot_process.stdin.flush()

            response = non_blocking_read()
            print(f"Received response from chatbot: {response}")

            if response:
                emit('bot_response', response)
            else:
                emit('bot_response', 'No response from chatbot.')
        except Exception as e:
            emit('bot_response', f'Error communicating with chatbot: {e}')
            print(f"Error communicating with chatbot: {e}")
    else:
        print("Chatbox is not running, starting now.")
        if start_chatbox():
            emit('bot_response', 'Chatbox is starting, please wait.')
        else:
            emit('bot_response', 'Failed to start the chatbox.')


if __name__ == '__main__':
    if start_chatbox():
        print("Chatbox is running.")
    else:
        print("Failed to start the chatbox process.")

    socketio.run(app, host='0.0.0.0', port=8765, debug=True)
