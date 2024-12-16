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
import select
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
socketio = SocketIO(app, message_queue='redis://127.0.0.1:6379', async_mode='gevent')  # Changed to gevent

# Global variable to store the chatbot process
chatbot_process = None
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
            universal_newlines=True  # Set universal_newlines=True to read as text, not bytes
        )
        print("Chatbox process started successfully.")

        # Wait for the chatbot to print "READY"
        while True:
            output_line = chatbot_process.stdout.readline().strip()
            if "READY" in output_line:
                print("Chatbox is ready.")
                break
            if chatbot_process.poll() is not None:
                print("Chatbox process exited before ready.")
                return False

        return True
    except Exception as e:
        print(f"Error starting chatbox process: {e}")
        return False


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


def non_blocking_read(output):
    ready, _, _ = select.select([output], [], [], 5.0)  # 5 seconds timeout
    if ready:
        return output.read().decode('utf-8').strip()
    else:
        return "No response in time."


@socketio.on('chat_message')
def handle_message(data):
    ip_address = request.remote_addr
    log_request(ip_address, data)

    if chatbot_process and chatbot_process.poll() is None:
        try:
            print("Sending data to chatbot:", data)
            chatbot_process.stdin.write(data + '\n')  # Remove .encode('utf-8') and use plain string
            chatbot_process.stdin.flush()

            # Wait for the response
            response = non_blocking_read(chatbot_process.stdout)
            print("Received response from chatbot:", response)

            if response:
                emit('bot_response', response)
                print(f"Emitting bot response: {response}")
            else:
                print("No response received or empty response.")
        except Exception as e:
            emit('bot_response', f'Error communicating with chatbot: {e}')
            print(f"Error communicating with chatbot: {e}")
    else:
        print("Chatbox is not running, starting now.")
        if start_chatbox():  # Start the chatbox if it's not running
            emit('bot_response', 'Chatbox is starting, please wait.')
        else:
            emit('bot_response', 'Failed to start the chatbox.')


def check_inactivity():
    global last_activity_time
    while True:
        if time.time() - last_activity_time > 1800:  # 30 minutes
            print("Closing connection due to inactivity")
            socketio.stop()  # Stop the SocketIO server
            break
        time.sleep(60)


if __name__ == '__main__':
    # Start the chatbox
    if start_chatbox():
        print("Chatbox is running.")
    else:
        print("Failed to start the chatbox process.")

    # Send a dummy message "Hello" to the chatbot for testing
    if chatbot_process and chatbot_process.poll() is None:
        try:
            print("Sending test message to chatbot: Hello")
            chatbot_process.stdin.write(b"Hello\n")
            chatbot_process.stdin.flush()
            print("Test message sent successfully.")
        except Exception as e:
            print(f"Error sending test message to chatbot: {e}")
    else:
        print("Chatbox is not running.")

    # Run the Flask app with gevent
    socketio.run(app, host='0.0.0.0', port=8765, debug=True)
