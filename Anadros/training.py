import random  # Used for shuffling and random operations
import json  # Used for working with JSON data
import pickle  # Used for serializing and deserializing Python objects
import numpy as np  # Used for numerical operations, especially with arrays
import nltk  # Natural Language Toolkit for text processing tasks
from nltk.stem import WordNetLemmatizer  # Used to reduce words to their base forms (lemmas)
from tensorflow.keras.models import Sequential  # Used to create a sequential model in Keras
from tensorflow.keras.layers import Dense, Activation, Dropout  # Layers for building the neural network model
from tensorflow.keras.optimizers.legacy import SGD as legacy_SGD  # An older version of the SGD optimizer
import mysql.connector  # Used to connect to and interact with a MySQL database

# Database configuration
# This dictionary holds the details required to connect to the MySQL database.
db_config = {
    'host': 'db-nadrd-01-do-user-15796887-0.f.db.ondigitalocean.com',
    'user': 'doadmin',
    'password': 'AVNS_xUEYPj9LdMHqRGNwHg5',
    'database': 'defaultdb',
    'port': 25060
}

# Connect to the database using the configuration provided.
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()  # Create a cursor object to interact with the database

# Fetch data from the database
# Execute a SQL query to fetch the 'tag', 'patterns', and 'responses' columns from the 'intents' table.
cursor.execute("SELECT tag, patterns, responses FROM intents")
intents_data = cursor.fetchall()  # Fetch all results from the executed query

# Close the database connection
cursor.close()  # Close the cursor to free up resources
conn.close()  # Close the database connection

# Prepare intents dictionary
# Initialize an empty dictionary to hold the intents data.
intents = {'intents': []}

# Process fetched data and structure it into the intents dictionary
for tag, patterns, responses in intents_data:
    pattern_list = json.loads(patterns)  # Convert the JSON string of patterns to a Python list
    response_list = json.loads(responses)  # Convert the JSON string of responses to a Python list

    intent = {
        'tag': tag,  # Intent tag (e.g., greeting, goodbye)
        'patterns': pattern_list,  # List of patterns (user inputs)
        'responses': response_list  # List of responses corresponding to the tag
    }
    intents['intents'].append(intent)  # Add the intent dictionary to the intents list

# Write intents data to intents.json without unnecessary characters
# Save the structured intents data to a JSON file with proper indentation and without ASCII encoding.
with open('intents.json', 'w') as file:
    json.dump(intents, file, indent=2, ensure_ascii=False)

# Initialize lemmatizer
# This object will convert words to their base forms, making pattern matching more effective.
lemmatizer = WordNetLemmatizer()

# Initialize lists for words, classes, and documents
words = []  # List to hold all words in the patterns
classes = []  # List to hold all unique intent tags
documents = []  # List to hold tuples of (pattern words, intent tag)
ignore_letters = ['?', '!', '.', ',']  # List of punctuation to ignore

# Process intents and patterns
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)  # Tokenize the pattern into individual words
        words.extend(word_list)  # Add the tokenized words to the words list
        documents.append((word_list, intent['tag']))  # Append the tuple (word_list, tag) to the documents list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])  # Add the intent tag to the classes list if not already present

# Preprocess words
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_letters]
words = sorted(set(words))  # Remove duplicates and sort the words alphabetically

# Preprocess classes
classes = sorted(set(classes))  # Sort the intent tags alphabetically

# Save processed data
# Save the words list to a pickle file for later use
pickle.dump(words, open('words.pkl', 'wb'))
# Save the classes list to a pickle file for later use
pickle.dump(classes, open('classes.pkl', 'wb'))

# Prepare training data
training = []  # List to hold training data
output_empty = [0] * len(classes)  # Initialize an output array with zeros for each class

for document in documents:
    bag = []  # Initialize an empty bag of words
    word_patterns = document[0]  # Get the word list from the document
    word_patterns = [lemmatizer.lemmatize(word.lower()) for word in word_patterns]  # Lemmatize each word
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)  # Create the bag of words vector

    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1  # Set the correct class index to 1 in the output array
    training.append([bag, output_row])  # Append the bag of words and output_row to the training data

# Shuffle and convert to numpy array
random.shuffle(training)  # Shuffle the training data to ensure randomization
train_x = np.array([i[0] for i in training])  # Convert the input data to a numpy array
train_y = np.array([i[1] for i in training])  # Convert the output data to a numpy array

# Build and compile the model
model = Sequential()  # Initialize a sequential model
model.add(
    Dense(128, input_shape=(len(train_x[0]),), activation='relu'))  # Input layer with 128 neurons and ReLU activation
model.add(Dropout(0.5))  # Dropout layer to prevent overfitting
model.add(Dense(64, activation='relu'))  # Hidden layer with 64 neurons and ReLU activation
model.add(Dropout(0.5))  # Another dropout layer
model.add(Dense(len(train_y[0]), activation='softmax'))  # Output layer with softmax activation

# Compile the model using legacy SGD optimizer
legacy_optimizer = legacy_SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=legacy_optimizer, metrics=['accuracy'])

# Train the model
hist = model.fit(np.array(train_x), np.array(train_y), epochs=100, batch_size=5,
                 verbose=1)  # Train the model with 100 epochs and batch size of 5

# Save the model in native Keras format
model.save('chatbotmodel.keras', hist)  # Save the trained model to a file

print("Done")  # Print a message indicating the process is complete
