from flask import Flask, render_template
import subprocess

app = Flask(__name__, template_folder='/var/www/my-site/Python-Chatbox/Anadros/AnadrosSite')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/train')
def train():
    # Run the training script
    print("Running training...")
    subprocess.run(['python3', '/var/www/my-site/Python-Chatbox/Anadros/training.py'])
    return "Training complete"

@app.route('/chat')
def chat():
    # Run the chatbot
    print("Starting chatbot...")
    subprocess.run(['python3', '/var/www/my-site/Python-Chatbox/Anadros/chatbox.py'])
    return "Chatbot started"

@app.route('/dynamic_content')
def dynamic_content():
    # You can put your dynamic content generation logic here
    dynamic_message = "This is a dynamic message from Flask!"
    return render_template('dynamic_content.html', dynamic_message=dynamic_message)

if __name__ == '__main__':
    app.run(debug=True)
