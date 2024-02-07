import os
import subprocess


# Function to run the training script
def run_training():
    try:
        print("Running training script...")
        subprocess.run(['python3', 'training.py'], check=True)
        print("Training completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running training script: {e}")


# Always run the training script before starting the chatbot
print("Running training...")
run_training()

# Run the chatbot
print("Starting chatbot...")
subprocess.run(['python3', 'chatbox.py'])
