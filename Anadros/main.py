import os
import subprocess
import requests


# Function to run the training script via Django view
def run_training_via_django():
    try:
        print("Running training script via Django view...")
        response = requests.get('http://127.0.0.1:8000/run_training/')
        print("Training completed successfully.")
    except requests.RequestException as e:
        print(f"Error occurred while running training script via Django view: {e}")


# Always run the training script before starting the chatbot
print("Running training...")
run_training_via_django()

# Run the chatbot
print("Starting chatbot...")
subprocess.run(['python3', 'chatbox.py'])
