import nltk
from nltk.corpus import wordnet as wn
import Question


def buildQuery(query, hyponyms=True, hypernyms=True):
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

def getKeyWords(question, stopWords):
    words = question.split(" ")
    keywords = []
    for w in words:
        if not w in stopWords:
            keywords.append(w)
    return keywords

def getStopWords():
    f = open("../stopWords.txt")
    words = f.readlines()
    f.close()
    words = map(lambda x: x.rstrip("\n"), words)
    s = set()
    for w in words:
        s.add(w)
    return s
            


################### Question Formatting Stuff Below (Declan) ##########


def findProximity(keywords, passage):
    """ Find the proximity of the keywords in the original document
    from each other in the passage. 
    Output: the total distance of all present keywords from each other
    and a dictionary containing <word1 word2>:<distance> pairs  """
    # Find positions of keywords in the passage
    lst = passage.split(" ")
    keywords.sort()
    wordIndices = {}
    numWords = 0
    totalDistance = 0
    allDistances = {}
    for i in range(len(lst)):
        w = lst[i]
        if w in keywords:
            # Count the number of different keywords in the passage
            if not w in wordIndices:
                numWords += 1
            wordIndices[w] = i
    # Find distance of all keywords from each other
    for i in range(len(keywords)-1):
        w1 = keywords[i]
        if w1 in wordIndices:
            for j in range(i+1, len(keywords)):
                w2 = keywords[j]
                if w2 in wordIndices:
                    pos1 = wordIndices[w1]
                    pos2 = wordIndices[w2]
                    distance = abs(pos1 - pos2)
                    totalDistance += distance
                    allDistances[w1+" "+w2] = distance
    return (numWords, totalDistance, allDistances)

def findAllProximities(keywords, passages):
    """ THIS IS A MAIN METHOD
    Input: a list of keywords from the question and a list of passages
    formatted as strings. Output: a list of tuples of
    <number of keywords that appeared in the passage>,<total distance> """
    proximityList = []
    for p in passages:
        (numWords, totalDistance, allDistances) = findProximity(keywords, p)
        proximityList.append((numWords, totalDistance))
    return proximityList

def getTagSequenceCounts(tagList, n):
    """ Input: tagList, a list of tags in the order they appeared.
    n, the maximum tag length that will be counted
    Output: tagSequenceCounts: <tag sequence>:<appearances> dictionary
    where tag sequence is a string of tags separated by spaces.
    The dictionary keeps counts of the appearances of all tag sequences
    of lengths 1...n
    Ignore the part where words are referred to as tags """
    tagSequenceCounts = {}
    for i in range(1, n+1):
        # Loop over all tag sequences of length i
        for j in range(len(tagList)-i+1): 
            tagSeq = tagList[j : j+i]
            tagString = listToString(tagSeq)
            # Add to table
            if tagString in tagSequenceCounts:
                tagSequenceCounts[tagString] += 1
            else:
                tagSequenceCounts[tagString] = 1
    return tagSequenceCounts

def buildNGrams(wordList, n):
    """ Builds a list of all n-grams in the given sentence.
    ngrams are formatted as "w1 w2 w3 ..." """
    gramList = []
    for i in range(len(wordList)-n+1):
        gram = wordList[i : i+n]
        # Convert list to string
        gramStr = reduce(lambda x,y: x+y+" ", gram, "").rstrip(" ")
        gramList.append(gramStr)
    return gramList

def countNGrams(ngrams, countDict):
    """ Return the total number of times all ngrams in ngrams (a list)
    appear in countDict """
    total = 0
    for ng in ngrams:
        if ng in countDict:
            total += countDict[ng]
    return total

def listToString(tagSeq):
    """ Input: a list of strings
    Output: a string of words separated by spaces """
    tagString = ""
    for t in tagSeq:
        tagString += t + " "
    return tagString.rstrip(" ")

def getNGramOverlap(question, passages, n):
    """ THIS IS A MAIN METHOD
    Input: the question and a list of passages
    in string format. For now I'm not doing any punctuation removal, etc.
    Output: a list of total distances between keywords and passages. """
    qList = question.split(" ")
    questionDict = getTagSequenceCounts(qList, n)
    overlapList = []
    for p in passages:
        words = p.split(" ")
        grams = buildNGrams(words, n)
        print grams
        count = countNGrams(grams, questionDict)
        overlapList.append(count)
    return overlapList
