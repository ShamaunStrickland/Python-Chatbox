from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import json
import requests
import time
import os
import threading
import select

app = Flask(__name__, template_folder='AnadrosSite', static_folder='static')
socketio = SocketIO(app)

# Global variable to store the chatbot process
chatbot_process = None
last_activity_time = time.time()


def start_chatbox():
    global chatbot_process
    dir_path = os.path.dirname(os.path.realpath(__file__))
    chatbox_script_path = os.path.join(dir_path, 'chatbox.py')
    try:
        chatbot_process = subprocess.Popen(['python3', chatbox_script_path], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Chatbox process started successfully.")
    except Exception as e:
        print(f"Error starting chatbox process: {e}")


def get_location(ip_address):
    url = f'http://ip-api.com/json/{ip_address}?fields=status,message,city,country,lat,lon'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                location = {
                    'city': data['city'],
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
    with open('request_logs.txt', 'a') as log_file:
        log_file.write(f'IP Address: {ip_address}\nLocation: {location}\nMessage: {message}\n\n')
    print(f'IP Address: {ip_address}, Location: {location}, Message: {message}')


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
            chatbot_process.stdin.write(data.encode('utf-8') + b'\n')
            chatbot_process.stdin.flush()
            response = non_blocking_read(chatbot_process.stdout)
            print("Received response from chatbot:", response)
            if response:
                emit('bot_response', response)
                print("Response sent to the client.")
            else:
                print("No response received or empty response.")
        except Exception as e:
            emit('bot_response', f'Error communicating with chatbot: {e}')
            print(f"Error communicating with chatbot: {e}")
    else:
        print("Chatbox is not running, starting now.")
        start_chatbox()  # Start the chatbox immediately
        emit('bot_response', 'Chatbox is starting, please wait.')


def check_inactivity():
    global last_activity_time
    while True:
        if time.time() - last_activity_time > 1800:  # 30 minutes
            print("Closing connection due to inactivity")
            socketio.stop()  # Stop the SocketIO server
            break
        time.sleep(60)


if __name__ == '__main__':
    start_chatbox()  # Start the chatbox immediately
    # Send a dummy message to the chatbox for testing
    dummy_message = "Hi, this is a test message from the Flask app."
    handle_message(dummy_message)
    inactivity_checker = threading.Thread(target=check_inactivity)
    inactivity_checker.start()
    socketio.run(app, host='0.0.0.0', port=8000)
