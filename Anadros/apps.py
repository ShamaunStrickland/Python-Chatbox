import subprocess
import re
import json
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import ssl
import time

app = Flask(__name__, template_folder='AnadrosSite', static_folder='static')

# Create SSL context
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain('/etc/nginx/ssl/ssl_certificate.pem', '/etc/nginx/ssl/ssl_certificate_key.pem')

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins=["https://anadros.com"], ssl_context=ssl_context,
                    logger=True, engineio_logger=True, engineio_logger_name=True)

# Global variable to store the chatbot process
chatbox_process = None
last_activity_time = time.time()


# Function to log IP addresses and chat messages
def log_request():
    ip_address = request.remote_addr
    location = get_location(ip_address)
    message = request.form.get('message')
    with open('request_logs.txt', 'a') as log_file:
        log_file.write(f'IP Address: {ip_address}\nLocation: {location}\nMessage: {message}\n\n')
    print(
        f'\033[91mIP Address: {ip_address}, Location: {location}, Message: {message}\033[0m')  # Print to console in red


# Function to get location from IP address
def get_location(ip_address):
    # API endpoint for IP Geolocation
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
            else:
                return 'Unknown'
        else:
            return 'Unknown'
    except Exception as e:
        print("Error getting location:", e)
        return 'Unknown'


# Function to start the chatbot process
def start_chatbot():
    global chatbox_process
    # Run chatbox script
    chatbox_script_path = 'chatbox.py'
    print("Running chatbot script:", chatbox_script_path)
    try:
        chatbox_process = subprocess.Popen(['python3', chatbox_script_path], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print("Error starting chatbot process:", e)


# Remove ANSI escape codes from the input text
def remove_ansi_escape_codes(text):
    return re.sub(r'(\x1b\[[0-9;]*m)|(\x1B\[[0-9;]*[HJ])', '', text)


# Start the chatbot process when the server starts
start_chatbot()


# Route for homepage
@app.route('/')
def index():
    log_request()  # Log IP address and message
    return render_template('index.html')


# Event handler for receiving messages from the frontend
@socketio.on('send_message')
def handle_message(data):
    global last_activity_time
    last_activity_time = time.time()  # Update last activity time
    log_request()  # Log IP address and message
    if chatbox_process is None:
        emit('bot_response', {'bot_response': 'Chatbot is not ready. Please wait.'})
        return

    user_input = data['message']

    # Send user input to chatbox script
    try:
        chatbox_process.stdin.write(user_input.encode('utf-8') + b'\n')
        chatbox_process.stdin.flush()
    except Exception as e:
        emit('bot_response', {'bot_response': f'Error sending message to chatbot: {e}'})
        return

    # Read the response from chatbox script
    try:
        bot_response = chatbox_process.stdout.readline().decode('utf-8').strip()
    except Exception as e:
        emit('bot_response', {'bot_response': f'Error reading response from chatbot: {e}'})
        return

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


# Function to periodically check for inactivity and close the connection
def check_inactivity():
    global last_activity_time
    while True:
        if time.time() - last_activity_time > 1800:  # Close connection after 30 minutes of inactivity
            print("Closing connection due to inactivity")
            socketio.disconnect()
            break
        time.sleep(60)  # Check every minute for inactivity


if __name__ == '__main__':
    # Start the Flask application
    try:
        # Start the inactivity checker in a separate thread
        import threading

        inactivity_checker = threading.Thread(target=check_inactivity)
        inactivity_checker.start()

        socketio.run(app, host='0.0.0.0', port=80, debug=True)
    except Exception as e:
        print("Error running Flask application:", e)
