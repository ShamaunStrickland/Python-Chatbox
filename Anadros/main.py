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

    # Run chatbot after training
    chatbox_script_path = os.path.join(current_dir, 'chatbox.py')
    print("Running chatbot script:", chatbox_script_path)
    subprocess.run(['python3', chatbox_script_path])
    return "Training complete and Chatbot started"

    return "Training complete"


@app.route('/chat')
def chat():
    # Run the chatbot
    chatbox_script_path = os.path.join(current_dir, 'chatbox.py')
    print("Running chatbot script:", chatbox_script_path)
    subprocess.run(['python3', chatbox_script_path])
    return "Chatbot started"


@app.route('/dynamic_content')
def dynamic_content():
    # You can put your dynamic content generation logic here
    dynamic_message = "This is a dynamic message from Flask!"
    return render_template('dynamic_content.html', dynamic_message=dynamic_message)


if __name__ == '__main__':
    app.run(debug=True)
