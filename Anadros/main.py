from flask import Flask, render_template
import subprocess
import os
import pymysql.cursors

# Initialize Flask app
app = Flask(__name__, template_folder='AnadrosSite')

# Database configuration
connection = pymysql.connect(host='anadros-user-training-data-do-user-15796887-0.c.db.ondigitalocean.com',
                             user='doadmin',
                             password='AVNS_eF16Y6-AumI0bR1dJvV',
                             database='defaultdb',
                             cursorclass=pymysql.cursors.DictCursor,
                             port=25060)


# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')


# Route for training the chatbot
@app.route('/train')
def train():
    # Run the training script
    training_script_path = 'training.py'
    print("Running training script:", training_script_path)
    subprocess.run(['python3', training_script_path])

    # Run chatbot after training
    chatbox_script_path = 'chatbox.py'
    print("Running chatbot script:", chatbox_script_path)
    subprocess.run(['python3', chatbox_script_path])
    return "Training complete and Chatbot started"


# Route for starting the chatbot
@app.route('/chat')
def chat():
    # Run the chatbot
    chatbox_script_path = 'chatbox.py'
    print("Running chatbot script:", chatbox_script_path)
    subprocess.run(['python3', chatbox_script_path])
    return "Chatbot started"


# Route for dynamic content
@app.route('/dynamic_content')
def dynamic_content():
    dynamic_message = "This is a dynamic message from Flask!"
    return render_template('dynamic_content.html', dynamic_message=dynamic_message)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
