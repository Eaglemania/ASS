##add nltk and pyaml to the project
import random, os, re, operator
from nltk.util import ngrams
from importlib import import_module
class generate():
    def __init__(self):
        pass
        
    def generate_name(self, length):
        words = self.generate_words(self.load_text())
        trigrams = self.generate_ngrams(3, words)
        word = list(trigrams[random.randint(0, len(trigrams))])       
        while len(word) < length:
            options = []
            for i in trigrams:
                if word[-2] == i[0] and word[-1] == i[1]:
                    options.append(i)
            try:
                option = random.choice(options)
                word.append(option[-1])
            except:
                pass            
                


        return "".join(word)
                
        
    def generate_text(self, amount, length):
        pass
    
    def generate_ngrams(self, grams, words):        
        result = []
        for w in words:
            items = ngrams(list(w), grams)
            for i in items:
                if i not in result:
                    result.append(i)            
        return result
    
    def generate_words(self, text):
        words = []
        for i in text.split():
            if i not in words and len(i) > 2:
                words.append(i)
        return words
    
    def load_text(self):
        files = os.listdir(os.getcwd())
        text = ""

        for f in files:
            if f[-3:] == ".py":
                with open(f, "r") as t:
                    text += t.read()
        processedText = []
        for m in re.finditer('"""(.*?)"""', text, re.S):
            processedText.append(m.group(1))
        for m in re.finditer('#(.*)', text):
            processedText.append(m.group(1))
        processedText = "\n".join(processedText)
        processedText = re.sub('[()\':#?!._,"\*/=\'\-\+\[\]]', ' ', processedText)
        return processedText

##usage example
"""
stuff = generate()
print stuff.generate_name(7)
"""
