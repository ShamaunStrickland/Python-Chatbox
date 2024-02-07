import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers.legacy import SGD as legacy_SGD

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Load intents data
intents = json.loads(open('intents.json').read())

# Initialize lists
words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

# Process intents and patterns
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

# Save intents data
with open('intents_processed.json', 'w') as file:
    json.dump(intents, file)

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

legacy_optimizer = legacy_SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=legacy_optimizer, metrics=['accuracy'])

# Train the model
hist = model.fit(np.array(train_x), np.array(train_y), epochs=100, batch_size=5, verbose=1)

# Save the model in native Keras format
model.save('chatbotmodel.keras', hist)

print("Done")
