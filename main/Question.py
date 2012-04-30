import gzip
from nltk import word_tokenize, pos_tag, ne_chunk

class Question():
    def __init__(self,number,desc,docs):
        self.number = number
        self.desc = desc
        
        # This needs to be initialized correctly
        self.desc_ne_chunks = self.ne_extraction(self.desc)
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
    
    def intersection_length(self, list1, list2):
        return len(set(list1)&set(list2))

    def string_intersection_length(self, str1, str2):
        return self.intersection_length(str1.split(' '), str2.split(' '))
    
    def ne_extraction(self, text):
        tags = pos_tag(text.split(' '))
        return ne_chunk(tags)
        
    def NE_rank(self, passages, named_entities):
        return map(self.intersection_length, map(self.ne_extraction, passages), \
                   [self.desc_ne_chunks] * len(passages))
    

    def num_keywords_rank(self, passages):
        return map(self.string_intersection_length , passages, [self.desc]*len(passages))
    
    # Implement soon
    def exact_sequence_rank(self, passages):
        pass
    
    # All punctuation should be separated by a space from the word 
    # it was attached to
    def rank_passages(self, passages, named_entities):
        rankings = zip(self.NE_rank(passages, named_entities), self.num_keywords_rank(passages), \
                       self.exact_sequence_rank(passages), self.document_rank(passages), \
                       self.proximity_rank(passages), self.ngram_overlap_rank(passages))
        return map(lambda x: float(sum(x)) / float(len(x)), rankings)
    
    def extract_documents(self):
        query = self.get_query()
        return self.run_IR()
        
    def run_baseline(self):
        q_tokens = word_tokenize(self.desc)[:-1] #remove "?"
        best_matches = [(0,"","")]*5
        tokens = []
        count = 0
        currentDoc = ""
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
            try:
                doc_index = input.index("DOCNO")
                currentDoc = input[doc_index+2]
            except ValueError: #"<DOCNO>" not in group
                pass
            except IndexError: #<DOCNO> at end of group
                if input.index("DOCNO") == 8:
                    currentDoc = tokens[0]
                else:
                    currentDoc = tokens[1]
            score = 0
            for q_token in q_tokens:
                if q_token in input:
                    score += 1
            for i in range(len(best_matches)):
                (top_score,doc,txt) = best_matches[i]
                if score > top_score:
                    best_matches[i] = (score,currentDoc,' '.join(input))
                    break
        return best_matches
        #return "Aleksei A. Leonov was the first dude"
            