from flask import Flask, render_template
import subprocess
import os

# Get the directory of main.py
current_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder=os.path.join(current_dir, 'AnadrosSite'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/train')
def train():
    # Run the training script
    training_script_path = os.path.join(current_dir, 'training.py')
    print("Running training script:", training_script_path)
    subprocess.run(['python3', training_script_path])
    return "Training complete"


@app.route('/chat')
def chat():
    # Run the chatbot
    chatbox_script_path = os.path.join(current_dir, 'chatbox.py')
    print("Running chatbot script:", chatbox_script_path)
    subprocess.run(['python3', chatbox_script_path])
    return "Chatbot started"
