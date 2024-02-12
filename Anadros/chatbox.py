import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers.legacy import SGD as legacy_SGD
from TerminalInterface import TerminalInterface
import os
import subprocess
import re

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# File paths
intents_file_path = 'intents.json'
responses_file_path = 'responses.json'
model_file_path = 'chatbotmodel.keras'
words_file_path = 'words.pkl'
classes_file_path = 'classes.pkl'

# Load or initialize intents data
try:
    with open(intents_file_path, 'r') as intents_file:
        intents = json.load(intents_file)
except FileNotFoundError:
    intents = {'intents': []}

# Load or initialize existing responses or create an empty dictionary if it doesn't exist
try:
    with open(responses_file_path, 'r') as responses_file:
        responses = json.load(responses_file)
except FileNotFoundError:
    responses = {}
    print("responses.json not found. Initializing empty responses.")

# Load existing model or create a new one
words = []
classes = []

try:
    model = load_model(model_file_path)
    # Load processed data
    with open(words_file_path, 'rb') as words_file:
        words = pickle.load(words_file)
    with open(classes_file_path, 'rb') as classes_file:
        classes = pickle.load(classes_file)
except FileNotFoundError:
    documents = []
    ignore_letters = ['?', '!', '.', ',']

    # Rest of the code...

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            word_list = nltk.word_tokenize(pattern)
            words.extend(word_list)
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # Preprocess words
    words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
    words = sorted(set(words))

    # Preprocess classes
    classes = sorted(set(classes))

    # Save processed data
    with open(words_file_path, 'wb') as words_file:
        pickle.dump(words, words_file)
    with open(classes_file_path, 'wb') as classes_file:
        pickle.dump(classes, classes_file)

    # Prepare training data
    training = []
    output_empty = [0] * len(classes)

    for document in documents:
        bag = []
        word_patterns = document[0]
        word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]
        for word in words:
            bag.append(1) if word in word_patterns else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(document[1])] = 1
        training.append([bag, output_row])

    # Shuffle and convert to numpy array
    random.shuffle(training)
    train_x = np.array([i[0] for i in training])
    train_y = np.array([i[1] for i in training])

    # Build and compile the model
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))

    # Use the legacy SGD optimizer
    optimizer = legacy_SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    # Train the model
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=1000, batch_size=5, verbose=1)

    # Save the model
    model.save(model_file_path, hist)


# Function to clean up a sentence
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


# Function to create a bag of words from a sentence
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


# Function to predict the class of a sentence
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)

    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]].lower(), 'probability': str(r[1])})
    return return_list


# Function to get a response based on the predicted intent
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
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
    intents['intents'].append(new_intent)

    # Save the updated intents to a file
    with open(intents_file_path, 'w') as intents_file:
        json.dump(intents, intents_file, indent=4)

    # Run the main script
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
cli = TerminalInterface()

while True:
    message = cli.get_user_input().lower()  # Convert user input to lowercase

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
        save_intent(new_intent_tag, patterns, responses)
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
        ints = predict_class(message)

        # Get the response based on the predicted intent
        res = get_response(ints, intents)

        # Check if the predicted intent is not found in the list of defined intents
        if not any(intent['tag'].lower() == ints[0]['intent'].lower() for intent in intents['intents']):
            cli.bot_response("Sorry, I didn't understand that.")
            user_correction = cli.get_user_input("Could you please provide the correct response for this input? ")
            save_response(ints[0]['intent'], message, user_correction)
            cli.bot_response("Thank you! I'll remember that.")
        else:
            # Display the response
            cli.bot_response(res)
