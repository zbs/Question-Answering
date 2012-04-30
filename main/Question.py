import gzip, xapian
from nltk import word_tokenize

class Question():
    def __init__(self,number,desc,docs):
        self.number = number
        self.desc = desc
        self.docs = gzip.open(docs)
        self.db_directory = "../db/db" + str(number)
        self.index_documents()

    def get_keywords(self):
        pass
    
    def reformulate_query(self, keywords):
        return ' '.join(keywords)
    
    def get_query(self):
        keywords = self.get_keywords()
        return self.reformulate_query(keywords)
    
    #Create IR database
    #bgj9
    def index_documents(self):
        # Open the database for update, creating a new database if necessary.
        database = xapian.WritableDatabase(self.db_directory, xapian.DB_CREATE_OR_OPEN)
        
        indexer = xapian.TermGenerator()
        stemmer = xapian.Stem("english")
        indexer.set_stemmer(stemmer)
        #for each document
        for doc_string in self.docs.read().split('\n\n'):
            doc = xapian.Document()
            doc.set_data(doc_string)
            
            indexer.set_document(doc)
            indexer.index_text(doc_string)
            
            database.add_document(doc)
    
    #search the IR database, returns a xapian mset
    #For query syntax: http://xapian.org/docs/queryparser.html
    #bgj9
    def search(self, query_string):
        # Open the database for searching.
        database = xapian.Database(self.db_directory)
    
        # Start an enquire session.
        enquire = xapian.Enquire(database)
    
        # Parse the query string to produce a Xapian::Query object.
        qp = xapian.QueryParser()
        stemmer = xapian.Stem("english")
        qp.set_stemmer(stemmer)
        qp.set_database(database)
        qp.set_stemming_strategy(xapian.QueryParser.STEM_SOME)
        query = qp.parse_query(query_string)
        #query = qp.parse_query(query_string, xapian.QueryParser.FLAG_AUTO_MULTIWORD_SYNONYMS)
        print "Parsed query is: %s" % str(query)
    
        # Find the top 10 results for the query.
        enquire.set_query(query)
        matches = enquire.get_mset(0, 10)
    
        # Display the results.
        print "%i results found." % matches.get_matches_estimated()
        print "Results 1-%i:" % matches.size()
    
        #for m in matches:
        #    print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
        return matches
    
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
            