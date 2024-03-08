# views.py
from django.http import HttpResponse
from django.shortcuts import render
import os
import subprocess


# Function to run the training script
def run_training(request):
    try:
        print("Running training script...")
        subprocess.run(['python3', 'training.py'], check=True)
        print("Training completed successfully.")
        return HttpResponse("Training completed successfully.")
    except subprocess.CalledProcessError as e:
        error_message = f"Error occurred while running training script: {e}"
        print(error_message)
        return HttpResponse(error_message)
