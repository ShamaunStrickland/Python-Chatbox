from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import subprocess
import json
import requests
import time
import threading

app = Flask(__name__, template_folder='AnadrosSite', static_folder='static')
socketio = SocketIO(app)

# Global variable to store the chatbot process
chatbot_process = None
last_activity_time = time.time()


def start_chatbot():
    global chatbot_process
    chatbot_script_path = 'chatbot.py'
    try:
        chatbot_process = subprocess.Popen(['python3', chatbot_script_path], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print("Error starting chatbot process:", e)


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
        print("Error getting location:", e)
        return 'Unknown'


def log_request(ip_address, message):
    location = get_location(ip_address)
    with open('request_logs.txt', 'a') as log_file:
        log_file.write(f'IP Address: {ip_address}\nLocation: {location}\nMessage: {message}\n\n')
    print(f'\033[91mIP Address: {ip_address}, Location: {location}, Message: {message}\033[0m')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    global last_activity_time
    last_activity_time = time.time()


@socketio.on('chat_message')
def handle_message(data):
    ip_address = request.remote_addr
    log_request(ip_address, data)
    if chatbot_process:
        try:
            chatbot_process.stdin.write(data.encode('utf-8') + b'\n')
            chatbot_process.stdin.flush()
            response = chatbot_process.stdout.readline().decode('utf-8').strip()
            emit('bot_response', response)
        except Exception as e:
            emit('bot_response', f'Error communicating with chatbot: {e}')
    else:
        emit('bot_response', 'Chatbot is not ready. Please wait.')


def check_inactivity():
    global last_activity_time
    while True:
        if time.time() - last_activity_time > 1800:  # 30 minutes
            print("Closing connection due to inactivity")
            socketio.stop()  # Stop the SocketIO server
            break
        time.sleep(60)


if __name__ == '__main__':
    start_chatbot()
    inactivity_checker = threading.Thread(target=check_inactivity)
    inactivity_checker.start()
    socketio.run(app, host='0.0.0.0', port=8000)
