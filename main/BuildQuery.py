import nltk
from nltk.corpus import wordnet as wn
import Question


def buildSynset(query, hyponyms=True, hypernyms=True):
    """ Input: the query string.
    Output: list of words
    Gets the part of speech of words in the query then finds synsets for 
    the "important" ones. Returns the words in those synsets. Can optionally
    return the hyopnyms and hypernyms of a word. """
    importantTags = ["JJ", "NNP", "NN", "VBN"]
    token = nltk.word_tokenize(query)
    posTags = nltk.pos_tag(token)
    # Find "important" tags and get synsets
    synsets = []
    for (word, tag) in posTags:
        if tag in importantTags:
            if tag == "JJ":
                t = wn.ADJ
            elif tag == "NNP" or tag == "NN":
                t = wn.NOUN
            elif tag == "VBN":
                t = wn.VERB
            try:
                syn = wn.synsets(word, pos=t)
            except KeyError:
                print "not in synsets"
                continue
            synsets.append(syn)
    # Build list of words from synsets
    synonyms = []
    for syn in synsets:
        for lemma in syn:
            word = lemma.name.split(".")[0]
            if not word in synonyms:
                synonyms.append(word)
            if hyponyms:
                synonyms = addCategory(synonyms, lemma)
            if hypernyms:
                synonyms = addCategory(synonyms, lemma, hyponym=False)
    return synonyms

def addCategory(synList, lemma, hyponym=True):
    """ Add all hyponyms or hypernyms to synList """
    if hyponym:
        nymList = lemma.hyponyms()
    else:
        nymList = lemma.hypernyms()
    for hypo in nymList:
        n = hypo.name
        word = n.split(".")[0].replace("_", " ")
        if not word in synList:
            synList.append(word)
    return synList

def getQuestions():
    """ Builds a list of questions formatted as (docNumber, question text) """
    f = open("../questions.txt")
    text = f.readlines()
    f.close()
    questions = []
    docNumber = -1
    qText = ""
    for i in range(len(text)):
        if text[i][0:5] == "<num>":
            num = int(text[i].rstrip("\n").split(" ")[2])
        elif text[i][0:6] == "<desc>":
            qText = text[i+1].rstrip("\n").rstrip("?")
            questions.append((num, qText))
    return questions



def buildQueries():
    stopWords = Question.STOP_WORDS
    questions = getQuestions()
    fullQuestions = []
    for i in range(len(questions)):
        num, q = questions[i]
        kw = Question.getKeyWords(q, stopWords)
        kwString = " ".join(kw)
        fullQuestions.append((num, q+" "+kwString))
    """
    for (num, q) in questions:
        synset = buildSynset(q, hyponyms=False)
        synString = " ".join(synset)
        fullQuestions.append((num, q+" "+synString))
    """
    return fullQuestions    
            
def trimSynset(query, synset):
    """ Removes overlap between query and synset """
    for s in synset:
        if s in query:
            synset.remove(s)
    return synset
    

