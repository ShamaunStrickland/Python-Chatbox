import eventlet

eventlet.monkey_patch(all=True)  # Make sure this is the very first line

import random  # Used for random operations, such as choosing a random response
import json  # Used for handling JSON files
import pickle  # Used for serializing and deserializing Python objects
import numpy as np  # Used for numerical operations, especially with arrays
import nltk  # Natural Language Toolkit for text processing tasks
from nltk.stem import WordNetLemmatizer  # Used to reduce words to their base forms (lemmas)
from tensorflow import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Dropout  # Layers for the neural network model
from keras.optimizers import SGD as legacy_SGD  # SGD optimizer, not part of the legacy module anymore
from TerminalInterface import TerminalInterface  # Assuming a custom module for handling terminal inputs/outputs
import os  # Used for interacting with the operating system (e.g., clearing terminal)
import subprocess  # Used for running external processes, like running a Python script
import re  # Regular expressions for pattern matching in strings
import mysql.connector  # Used for connecting to and interacting with a MySQL database
from db_config import db_config

# Connect to the database using the configuration provided.
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)  # Cursor object to interact with the database

# Suppress TensorFlow warnings
# The environment variable 'TF_CPP_MIN_LOG_LEVEL' is set to '3' to hide all but the most severe TensorFlow warnings.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize the lemmatizer, which will convert words to their base forms (e.g., "running" to "run").
lemmatizer = WordNetLemmatizer()

# File paths for storing various data related to the chatbot.
intents_file_path = 'intents.json'
responses_file_path = 'responses.json'
model_file_path = 'chatbotmodel.keras'
words_file_path = 'words.pkl'
classes_file_path = 'classes.pkl'


# Function to clean up unnecessary terminal output by clearing the terminal screen.
def clean_terminal():
    os.system('clear' if os.name == 'posix' else 'cls')


# Clean terminal before starting the chatbot
clean_terminal()

# Load or initialize intents data
try:
    # Try to open and load the intents JSON file.
    with open(intents_file_path, 'r') as intents_file:
        intents = json.load(intents_file)
except FileNotFoundError:
    # If the file doesn't exist, initialize an empty intents dictionary.
    intents = {'intents': []}

# Load or initialize existing responses or create an empty dictionary if it doesn't exist
try:
    # Try to open and load the responses JSON file.
    with open(responses_file_path, 'r') as responses_file:
        responses = json.load(responses_file)
except FileNotFoundError:
    # If the file doesn't exist, initialize an empty responses dictionary.
    responses = {}
    print("responses.json not found. Initializing empty responses.")

# Load existing model or create a new one
words = []
classes = []

try:
    # Try to load the existing trained model.
    model = load_model(model_file_path)
    # Load processed words and classes data from their respective files.
    with open(words_file_path, 'rb') as words_file:
        words = pickle.load(words_file)
    with open(classes_file_path, 'rb') as classes_file:
        classes = pickle.load(classes_file)
except FileNotFoundError:
    # If model files are not found, start building a new model.
    documents = []
    ignore_letters = ['?', '!', '.', ',']  # List of characters to ignore during tokenization

    # Rest of the code for processing intents

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)  # Tokenize each pattern into words
            words.extend(word_list)  # Add words to the list
            documents.append((word_list, intent['tag']))  # Pair words with their corresponding intent tags
            if intent['tag'] not in classes:
                classes.append(intent['tag'])  # Add unique intent tags to the classes list

    # Preprocess words
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
    words = sorted(set(words))  # Remove duplicates and sort the words

    # Preprocess classes
    classes = sorted(set(classes))  # Sort the intent classes

    # Save processed data
    with open(words_file_path, 'wb') as words_file:
        pickle.dump(words, words_file)  # Save the words list as a binary file
    with open(classes_file_path, 'wb') as classes_file:
        pickle.dump(classes, classes_file)  # Save the classes list as a binary file

    # Prepare training data
    training = []
    output_empty = [0] * len(classes)  # Create an empty output array with zeros

    for document in documents:
        bag = []  # Initialize an empty bag of words
        word_patterns = document[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
        for word in words:
            bag.append(1) if word in word_patterns else bag.append(0)  # Create a bag of words vector

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1  # Set the correct index in the output array to 1
        training.append([bag, output_row])  # Add the bag of words and the output array to the training data

    # Shuffle and convert to numpy array
    random.shuffle(training)
    train_x = np.array([i[0] for i in training])  # Convert the training data to numpy arrays
    train_y = np.array([i[1] for i in training])

    # Build and compile the model
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))  # Input layer
    model.add(Dropout(0.5))  # Dropout for regularization
    model.add(Dense(64, activation='relu'))  # Hidden layer
    model.add(Dropout(0.5))  # Dropout for regularization
    model.add(Dense(len(train_y[0]), activation='softmax'))  # Output layer

    # Use the legacy SGD optimizer
    optimizer = legacy_SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    # Train the model
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=1000, batch_size=5, verbose=1)

    # Save the model
    model.save(model_file_path, hist)


# Function to clean up a sentence
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)  # Tokenize the sentence into words
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]  # Lemmatize each word
    return sentence_words


# Function to create a bag of words from a sentence
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)  # Initialize a bag of words vector with zeros
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1  # Set the corresponding index in the bag to 1 if the word is found
    return np.array(bag)


# Function to predict the class of a sentence
def predict_class(sentence):
    bow = bag_of_words(sentence)  # Convert the sentence to a bag of words
    res = model.predict(np.array([bow]), verbose=0)[0]  # Predict the class probabilities
    ERROR_THRESHOLD = 0.25  # Set a threshold to filter out low-confidence predictions
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)  # Sort results by probability in descending order

    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]].lower(),
                            'probability': str(r[1])})  # Append the intent and probability to the return list
    return return_list


# Function to get a response based on the predicted intent
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']  # Get the intent with the highest probability
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])  # Choose a random response associated with the intent
            break
    else:
        result = "Sorry, I didn't understand that."
    return result


# Function to save new intents and patterns to the intents file
def save_intent(intent_tag, patterns, responses):
    new_intent = {
        "tag": intent_tag,
        "patterns": patterns,
        "responses": responses
    }
    intents['intents'].append(new_intent)  # Append the new intent to the intents list

    # Save the updated intents to a file
    with open(intents_file_path, 'w') as intents_file:
        json.dump(intents, intents_file, indent=4)

    # Run the main script to apply the changes
    subprocess.run(['python3', 'main.py'], check=True)


# Function to evaluate mathematical expressions
def evaluate_math_expression(expression):
    try:
        # Remove non-mathematical characters
        expression = re.sub(r'[^\d\.\+\-\*/\(\)]', '', expression)
        # Evaluate the expression
        result = eval(expression)
        return result
    except Exception as e:
        print(f"Error occurred while evaluating math expression: {e}")
        return None


# Instantiate TerminalInterface
cli = TerminalInterface()  # This is a custom class to handle terminal interactions


# Function to check credentials in the database
def check_credentials(username, password):
    query = "SELECT * FROM login WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))  # Execute the SQL query with provided username and password
    return cursor.fetchone() is not None  # Return True if a matching record is found, otherwise False


# Function to create a new user in the database
def create_new_user(username, password):
    query = "INSERT INTO login (username, password) VALUES (%s, %s)"
    cursor.execute(query, (username, password))  # Insert the new user's credentials into the database
    conn.commit()  # Commit the transaction to save changes


# Function to initiate login
def initiate_login():
    attempts = 3  # Number of login attempts allowed
    while attempts > 0:
        print("Would you like to login? (yes/no): ")
        login_choice = cli.get_user_input().lower()
        if login_choice == "yes":
            print("Enter your username and password: ")
            username = cli.get_user_input()  # Get the username from the user
            password = cli.get_user_input()  # Get the password from the user
            if check_credentials(username, password):
                print("Login successful!")
                return username  # Return the username if login is successful
            else:
                print("Invalid username or password.")
                create_account = cli.get_user_input(
                    "Would you like to create a new account? (yes/no): ").lower()
                if create_account == "yes":
                    new_username = cli.get_user_input("Enter a new username: ")
                    new_password = cli.get_user_input("Enter a new password: ")
                    create_new_user(new_username, new_password)  # Create a new user in the database
                    print("Account created successfully!")
                    return new_username  # Return the new username after account creation
                else:
                    return None
        elif login_choice == "no":
            print("Okay, continuing as guest.")
            return None  # Return None if the user chooses not to log in
        else:
            print("Invalid choice. Please enter 'yes' or 'no'.")
            attempts -= 1  # Decrease the number of attempts left
    print("Exceeded maximum login attempts. Exiting.")
    return None


# Main loop that runs continuously until the user exits
while True:
    message = cli.get_user_input().lower()  # Convert user input to lowercase

    # Check for login initiation
    if "login" in message:
        current_user = initiate_login()  # Start the login process
        if current_user:
            print("Welcome, " + current_user + "!")
        else:
            print("Continuing as guest.")
        continue  # Skip further processing after login attempt

    # If the user enters the "Force_Response" command
    if message == "force_response":
        print("Creating a new intent tag and patterns...")
        new_intent_tag = cli.get_user_input("Enter the new intent tag: ")
        patterns = []
        for i in range(3):
            pattern = cli.get_user_input(f"Enter pattern {i + 1}: ")
            patterns.append(pattern)
        responses = []
        for i in range(3):
            response = cli.get_user_input(f"Enter response {i + 1}: ")
            responses.append(response)
        save_intent(new_intent_tag, patterns, responses)  # Save the new intent and patterns
        print("New intent and patterns saved successfully!")
    else:
        # Check if the message contains mathematical expressions
        if any(op in message for op in ['+', '-', '*', '/']):
            # Evaluate mathematical expression
            result = evaluate_math_expression(message)
            if result is not None:
                # Display the result
                cli.bot_response("The result is: " + str(result))
                continue  # Skip further processing if it's a mathematical expression

        # Predict the intent
        ints = predict_class(message)  # Predict the user's intent based on the message

        # Get the response based on the predicted intent
        res = get_response(ints, intents)

        # Check if the predicted intent is not found in the list of defined intents
        if not any(intent['tag'].lower() == ints[0]['intent'].lower() for intent in intents['intents']):
            cli.bot_response("Sorry, I didn't understand that.")
            user_correction = cli.get_user_input("Could you please provide the correct response for this input? ")
            save_response(ints[0]['intent'], message, user_correction)  # Save the correct response for future use
            cli.bot_response("Thank you! I'll remember that.")
        else:
            # Display the response
            cli.bot_response(res)

# Ensure the chatbox_process variable is set to None
chatbox_process = None
