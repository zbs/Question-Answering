import gzip, xapian, re
from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup
import Ranker

WINDOW = 10
def getStopWords():
    f = open("../stopWords.txt")
    words = f.readlines()
    f.close()
    words = map(lambda x: x.rstrip("\n"), words)
    s = set()
    for w in words:
        s.add(w)
    return s

STOP_WORDS = getStopWords()

def getKeyWords(question, stopWords):
    words = question.split(" ")
    keywords = []
    for w in words:
        if not w in stopWords:
            keywords.append(w)
    return keywords

    
class Question():
    def __init__(self,number,desc,docs):
        self.number = number
        self.desc = desc
        
        # This needs to be initialized correctly
        self.docs = gzip.open(docs)
        
        self.doc_filename = docs
        self.db_directory = "../db/db" + str(number)
        self.index_documents()

    def getDocumentRelevantInfo(self):
        with gzip.open(self.doc_filename) as fp:
            text = fp.read()
        soup = BeautifulSoup(text)
        return map(lambda x: re.sub('\t|\s\s+|\n', ' ', x.getText()), \
                   soup('doc'))
    
    #splits documents into a list
    #also removes tags, newlines, tabs, extra spaces
    def splitByDOC(self):
        return self.getDocumentRelevantInfo()

    def get_keywords(self):
        pass
    
    def reformulate_query(self, keywords):
        return ' '.join(keywords)
    
    def get_query(self):
        keywords = self.get_keywords()
        return self.reformulate_query(keywords)
    
    #Create IR database using top 50 docs with tags stripped
    #bgj9
    def index_documents(self):
        # Open the database for update, creating a new database if necessary.
        print "Going through index_documents"
        database = xapian.WritableDatabase(self.db_directory, xapian.DB_CREATE_OR_OPEN)
        
        indexer = xapian.TermGenerator()
        stemmer = xapian.Stem("english")
        indexer.set_stemmer(stemmer)
        
        #for each document
        for doc_string in self.splitByDOC():
            doc = xapian.Document()
            doc.set_data(doc_string)
            
            indexer.set_document(doc)
            indexer.index_text(doc_string)
            
            database.add_document(doc)
    
    #search the IR database, returns a xapian mset
    #For query syntax: http://xapian.org/docs/queryparser.html
    #returns [(percent, doc_string)]
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
        #print "Parsed query is: %s" % str(query)
    
        # Find the top 10 results for the query.
        enquire.set_query(query)
        matches = enquire.get_mset(0, 10)
    
        # Display the results.
        print "%i results found." % matches.get_matches_estimated()
        print "Results 1-%i:" % matches.size()
        #for m in matches:
        #    print "%i: %i%% docid=%i [%s]" % (m.rank + 1, m.percent, m.docid, m.document.get_data())
        results = []
        for m in matches:
            results.append( (m.percent, m.document.get_data()) )
        return results

    
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
        
        
    def golden_passage_retriever( self, ir_results ):
        passages = []
        for (ranking, document) in ir_results:
            for sentence in sent_tokenize(document):
                tokens = word_tokenize(sentence)
                i = 0
                while (i < len(tokens)):
                    passages.append( (" ".join(tokens[i : i+WINDOW]), ranking) )
                    i += WINDOW / 2
        return passages
    
    def strip_tags(self, doc_string):
        return re.sub("<[^<>]+>", "", doc_string)
    
    def top5(self, passages):
        keywords = getKeyWords(self.desc, STOP_WORDS)
        return zip(*Ranker.rank_passages(self.desc, passages, keywords)[:5])[1]
            
    def test(self, passages):
        keywords = getKeyWords(self.desc, STOP_WORDS)
        print keywords
        for (p,_) in passages:
            print p+'\n'
        return Ranker.rank_passages(self.desc, passages, keywords)
            
#q = Question(227,0,"../docs/top_docs.227.gz")
#print (q.golden_passage_retriever(q.search("I think that's great!")))
