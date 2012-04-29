import gzip
from nltk import word_tokenize

class Question():
    def __init__(self,number,desc,docs):
        self.number = number
        self.desc = desc
        self.docs = gzip.open(docs)

    def get_keywords(self):
        pass
    
    def reformulate_query(self, keywords):
        return ' '.join(keywords)
    
    def get_query(self):
        keywords = self.get_keywords()
        return self.reformulate_query(keywords)

    def run_IR(self):
        # Interface with pyLemur here
        pass
    
    def extract_documents(self):
        query = self.get_query()
        return self.run_IR()
        
    def run_baseline(self):
        q_tokens = word_tokenize(self.desc)[:-1] #remove "?"
        best_match = []
        best_score = 0
        tokens = []
        count = 0
        for line in self.docs:
            count += 1
            if count > 1000: #gets thru over 10 documents
                break
            tokens += word_tokenize(line)
        while tokens:
            if len(tokens) > 10:
                input = tokens[:10]
                tokens = tokens[10:]
            else:
                input = tokens
                tokens = []
            score = 0
            for q_token in q_tokens:
                if q_token in input:
                    score += 1
            if score > best_score:
                best_score = score
                best_match = input
        return ' '.join(best_match)
        #return "Aleksei A. Leonov was the first dude"
            