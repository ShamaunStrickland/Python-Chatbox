import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
from TerminalInterface import TerminalInterface
import os

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load or initialize intents data
try:
    intents = json.loads(open('intents.json').read())
except FileNotFoundError:
    intents = {'intents': []}

# Load or initialize existing responses
try:
    responses = json.loads(open('responses.json').read())
except FileNotFoundError:
    responses = {}

# Load existing model or create a new one
words = []
classes = []

try:
    model = load_model('chatbotmodel.h5')
    # Load processed data
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
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
    pickle.dump(words, open('words.pkl', 'wb'))
    pickle.dump(classes, open('classes.pkl', 'wb'))

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

    sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

    # Train the model
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=1000, batch_size=5, verbose=1)

    # Save the model
    model.save('chatbotmodel.h5', hist)

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
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

# Function to get a response based on the predicted intent
def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

# Function to save new responses to the responses dictionary
def save_response(intent_tag, user_input, correct_response):
    if intent_tag not in responses:
        responses[intent_tag] = {}
    responses[intent_tag][user_input] = correct_response

    # Save the responses to a file
    with open('responses.json', 'w') as responses_file:
        json.dump(responses, responses_file, indent=4)

# Instantiate TerminalInterface
cli = TerminalInterface()

while True:
    message = cli.get_user_input()

    # Predict the intent
    ints = predict_class(message)

    # Get the response based on the predicted intent
    res = get_response(ints, intents)

    # If response is not recognized, ask for clarification
    if res == "Sorry, I didn't understand that.":
        cli.bot_response(res)
        user_correction = cli.get_user_input("Could you please provide the correct response for this input? ")
        save_response(ints[0]['intent'], message, user_correction)
        cli.bot_response("Thank you! I'll remember that.")

    else:
        # Display the response
        cli.bot_response(res)
