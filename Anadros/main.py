import subprocess
import os

# Run the training script
print("Running training...")
subprocess.run(['python3', 'training.py'])

# Run the chatbot
print("Starting chatbot...")
subprocess.run(['python3', 'chatbox.py'])
