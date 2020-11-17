import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

import tkinter as tk
from tkinter import *
from tkHyperlinkManager import *

import webbrowser
import json


class ChatBot:
    def __init__(self,master):
        self.master = master
        master.title("College Enquiry Chatbot")
        master.geometry("400x500")

        self.label = Label(master, text = "College Enquiry Chatbot")
        self.label.pack()

        self.ChatLog = Text(master, bd=0, bg="white", height="8", width="50", font="Verdana", wrap="word")
        self.ChatLog.config(state=DISABLED)

        #Bind scrollbar to Chat window
        self.scrollbar = Scrollbar(master, command=self.ChatLog.yview)
        self.ChatLog['yscrollcommand'] = self.scrollbar.set

        #Create Button to send message
        self.SendButton = tk.Button(master, font=("Verdana",12,'bold'), text="Send", width="8", height=3, bd=0, bg="#32de97", activebackground="#3c9d9b",fg='#ffffff', command= self.send )

        #Create the box to enter message
        self.EntryBox = Text(master, bd=0, bg="white",width="29", height="5", font="Verdana", wrap="word")
        self.EntryBox.bind("<Return>",master)

        # LAYOUT
        self.scrollbar.place(x=376,y=6, height=426)
        self.ChatLog.place(x=6,y=6, height=426, width=370)
        self.EntryBox.place(x=128, y=441, height=50, width=265)
        self.SendButton.place(x=6, y=441, height=50)

        # First message to ask information
        self.ChatLog.config(state=NORMAL)
        hyperlink = HyperlinkManager(self.ChatLog)
        self.msg = "Hey, I'm your bot. Ask me anything about Dayananda Sagar University. To get notified about our latest news "
        self.ChatLog.insert(INSERT, "Bot: " + self.msg)
        self.ChatLog.insert(END, "click here",hyperlink.add(self.click))
        self.ChatLog.insert(END, '\n\n')
        self.ChatLog.config(state=DISABLED)

    def click(self):
        webbrowser.open_new("http://127.0.0.1:5000")

    def clean_up_sentence(self, sentence):
        # tokenize the pattern - split words into array
        self.sentence_words = nltk.word_tokenize(sentence)
        # stem each word - create short form for word
        self.sentence_words = [lemmatizer.lemmatize(word.lower()) for word in self.sentence_words]
        return self.sentence_words

    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

    def bow(self, sentence, words, show_details=True):
        # tokenize the pattern
        self.sentence_words = self.clean_up_sentence(sentence)
        # bag of words - matrix of N words, vocabulary matrix
        self.bag = [0]*len(words)  
        for s in self.sentence_words:
            for i,w in enumerate(words):
                if w == s: 
                    # assign 1 if current word is in the vocabulary position
                    self.bag[i] = 1
                    if show_details:
                        print ("found in bag: %s" % w)
        return(np.array(self.bag))

    def predict_class(self, sentence, model):
        # filter out predictions below a threshold
        self.p = self.bow(sentence, words,show_details=False)
        self.res = model.predict(np.array([self.p]))[0]
        ERROR_THRESHOLD = 0.25
        self.results = [[i,r] for i,r in enumerate(self.res) if r>ERROR_THRESHOLD]
        # sort by strength of probability
        self.results.sort(key=lambda x: x[1], reverse=True)
        print(self.results)
        self.return_list = []
        for r in self.results:
            self.return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
        return self.return_list

    def getResponse(self, ints, intents_json):
        self.tag = ints[0]['intent']
        print(self.tag)
        self.list_of_intents = intents_json['intents']
        for i in self.list_of_intents:
            if(i['tag']== self.tag):
                self.result = random.choice(i['responses'])
                print(self.result)
                break
        return self.result


    def chatbot_response(self, msg):
        self.ints = self.predict_class(msg, model)
        if(len(self.ints)== 0):
            self.ints=[{'intent': 'idk'}]
        elif(float(self.ints[0]['probability'])<0.75):
            self.ints=[{'intent': 'idk'}]
        print(self.ints)
        
        self.res = self.getResponse(self.ints, intents)
        self.history(msg,self.res)
        return self.res

    def send(self,event=None):
        self.msg = self.EntryBox.get("1.0",'end-1c').strip()
        self.EntryBox.delete("0.0",END)

        if self.msg != '':
            self.ChatLog.config(state=NORMAL)
            self.ChatLog.insert(END, "You: " + self.msg + '\n\n')
            self.ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
        
            self.res = self.chatbot_response(self.msg)
            
            self.ChatLog.insert(END, "Bot: " + self.res + '\n\n')
            self.ChatLog.config(state=DISABLED)
            self.ChatLog.yview(END)
    
    def history(self,msg,response,filename='database.json'):
        with open('database.json') as json_file: 
            data = json.load(json_file) 
            temp = data['history'] 
            y = {"query":msg, 
                "response": response
                }        
            temp.append(y) 
        with open(filename,'w') as f: 
            json.dump(data, f, indent=4) 
        
    

if __name__ == '__main__':
    root = Tk()
    my_gui = ChatBot(root)
    root.mainloop()
    
    
