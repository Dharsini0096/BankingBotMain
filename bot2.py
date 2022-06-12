import nltk
nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer

import numpy
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.models import model_from_json
import random
import json
import pickle
from github import Github

stemmer = LancasterStemmer()


words = []
labels = []
doc_x = []
doc_y = []
data = {}
myChatModel = []


def getbankname(name):
    bank = name
    global data

    g = Github('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')
    user = g.get_user()

    repo = g.search_repositories("Dharsini0096/BankingBotMain")[0]


    with open(bank + ".json") as file:
        data = json.load(file)


    global words, labels, doc_x, doc_y

    try:
        with open(bank + "data.pickle", "rb") as f:
            words, labels, training, output = pickle.load(f)

    except FileNotFoundError:

        for intents in data["intents"]:
            for pattern in intents["pattern"]:
                wrds = nltk.word_tokenize(pattern)
                words.extend(wrds)
                doc_x.append(wrds)
                doc_y.append(intents["tag"])

            if intents["tag"] not in labels:
                labels.append(intents["tag"])

        words = [stemmer.stem(w.lower()) for w in words if w != "?"]
        words = sorted(list(set(words)))
        labels = sorted(labels)

        training = []
        output = []

        out_empty = [0 for _ in range(len(labels))]

        for x, doc in enumerate(doc_x):
            bag = []

            wrds = [stemmer.stem(w.lower()) for w in doc]
            for w in words:
                if w in wrds:
                    bag.append(1)
                else:
                    bag.append(0)

            output_row = out_empty[:]
            output_row[labels.index(doc_y[x])] = 1
            training.append(bag)
            output.append(output_row)

        training = numpy.array(training)
        output = numpy.array(output)

        with open(bank + "data.pickle", "wb") as f:
            pickle.dump((words, labels, training, output), f)

        with open(bank + "data.pickle", "rb") as f:
            sample = pickle.load(f)
            print(type(sample))
            repo.create_file(bank + "data.pickle", "Committing", str(sample))
            print("Pickle File created in repo")

    try:
        global myChatModel
        json_file = open(bank + 'chatbotmodel.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        myChatModel = model_from_json(loaded_model_json)
        myChatModel.load_weights(bank + "chatbotmodel.h5")
        print("Loaded model from disk")
    except Exception:
        myChatModel = Sequential()
        myChatModel.add(Dense(8, input_shape=[len(words)], activation='relu'))
        myChatModel.add(Dense(len(labels), activation='softmax'))

        myChatModel.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        myChatModel.fit(training, output, epochs=1000, batch_size=8)

        model_json = myChatModel.to_json()
        with open(bank + "chatbotmodel.json", "w") as y_file:
            y_file.write(model_json)

        #json_file = open(bank + 'chatbotmodel.json', 'r')

        repo.create_file(bank + "chatbotmodel.json", "Committing", str(model_json))
        print("Model File created in repo")

        weight = myChatModel.get_weights()
        repo.create_file(bank + "chatbotmodel.h5", "Committing", str(weight))
        print("H5 File created in repo")

        myChatModel.save_weights(bank + "chatbotmodel.h5")

        #myChatModel.load_weights(bank + "chatbotmodel.h5")
        #repo.create_file('master/ ' + bank + "chatbotmodel.h5", "Committing", myChatModel)
        #print("H5 File created in repo")
        print("Saved model from disk")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


def chatwithbot(inputtext):

    currenttext = bag_of_words(inputtext, words)
    currenttextarray = [currenttext]
    numpycurrenttext = numpy.array(currenttextarray)

    if numpy.all((numpycurrenttext == 0)):
        return "I didn't get that try again"

    results = myChatModel.predict(numpycurrenttext[0:1])
    results_index = numpy.argmax(results)
    tag = labels[results_index]

    if results[0][results_index] > 0.7:
        for tg in data['intents']:
            if tg['tag'] == tag:
                responses = tg['responses']

        return random.choice(responses)
    else:
        return "I didn't get that try again"


def chat():
    print("Start talking with bot (try quit to stop):")
    #bankname = input("Bankname : ")
    #getbankname(bankname)

    while True:
        inp = input("You:")
        if inp.lower() == "quit":
            break
        print(chatwithbot(inp))


#chat()
