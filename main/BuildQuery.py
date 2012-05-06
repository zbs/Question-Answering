import nltk
from nltk.corpus import wordnet as wn
import Question


def buildSynset(word, pos, hyponyms=True, hypernyms=True):
    """ Input: a word from the query string and its part of speech.
    Output: list of words
    Returns the synset of the given word. Optionally
    returns the hyopnyms and hypernyms of a word. """
    try:
        syn = wn.synsets(word, pos=pos)
    except KeyError:
        print "not in synsets"
        return []
    # Build list of words from synsets, hyponyms and hypernyms
    synonyms = []
    for lemma in syn:
        word = lemma.name.split(".")[0]
        if not word in synonyms:
            synonyms.append(word)
        if hyponyms:
            synonyms = addCategory(synonyms, lemma)
        if hypernyms:
            synonyms = addCategory(synonyms, lemma, hyponym=False)
        synonyms = editSpaces(synonyms)
    return synonyms

def buildFullQuery(query, hyponyms=True, hypernyms=True):
    importantTags = ["JJ", "NNP", "NN", "VBN"]
    token = nltk.word_tokenize(query)
    posTags = nltk.pos_tag(token)
    # Find "important" tags and get synsets
    queryParts = []
    synsets = []
    for (word, tag) in posTags:
        if tag in importantTags:
            if tag == "JJ":
                t = wn.ADJ
            elif tag == "NNP" or tag == "NN":
                t = wn.NOUN
            elif tag == "VBN":
                t = wn.VERB
            # Find synset of word:
            synset = buildSynset(word, t, hyponyms, hypernyms)
            if len(synset) != 0:
                queryParts.append("(" + " OR ".join(synset) + ")")
    if len(queryParts) != 0:
        expansion = " OR (" + " AND ".join(queryParts) + ")"
    else:
        expansion = ""
    return query.rstrip("?") + expansion

def addCategory(synList, lemma, hyponym=True):
    """ Add all hyponyms or hypernyms to synList """
    if hyponym:
        nymList = lemma.hyponyms()
    else:
        nymList = lemma.hypernyms()
    for hypo in nymList:
        n = hypo.name
        word = n.split(".")[0]
        if not word in synList:
            synList.append(word)
    return synList

def editSpaces(words):
    newWords = []
    for w in words:
        if "_" in w:
            w = '\"' + word.replace("_", " "), + '\"'
        newWords.append(w)
    return newWords

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
    

