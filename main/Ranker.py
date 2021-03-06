# NOTE, APPARENTLY WE NEED A MORE EFFICIENT WAY OF NE_CHUNKING, THE CURRENT ONE IS TOO SLOW
import urllib, operator
import urllib2, re
import json
WEIGHTS = (2.1, 1.6, 0.018, 90., 2.1, 30.0, 230., 2)

def dict_intersection_length(d1,d2):
    total = 0
    for key in d1:
        try:
            total += intersection_length(d1[key], d2[key])
        except KeyError:
            pass
    return total
    
def intersection_length(list1, list2):
    return len(set(list1)&set(list2))

def string_intersection_length(str1, str2):
    return intersection_length(str1.lower().split(' '), str2.lower().split(' '))

def ne_extract(text):
    url = "http://text-processing.com/api/phrases/"
    values = {'text': text}
    data = urllib.urlencode(values)
    response = urllib2.urlopen(url, data)
    return json.loads(response.read())
    

def NE_rank(question, passages):
    return map(dict_intersection_length, map(ne_extract, passages), \
               [ne_extract(question)] * len(passages))


def num_keywords_rank(question, passages):
    return map(string_intersection_length , passages, [question]*len(passages))

def exact_sequence_rank(question, passages):
    sequences = []
    fragments = question.split(' ')
    for i in range(0, len(fragments)):
        for j in range(i, len(fragments)+1):
            sequences.append(fragments[i:j])
    return map(lambda x: max(map(len, filter(lambda z: x.lower().find(' '.join(z).lower())!= -1, sequences))), passages)
        

def document_rank(passages_docs, passages):
    return map(lambda x: passages_docs[x], passages)


def dot(v1, v2):
    return reduce( operator.add, map( operator.mul, v1, v2))
    
def rank_passages(question, passages_tuple, keywords):
    """
        WORLDS WRST FUNCTON EVR
        passages: list of passages
        passage_rankings: passage --> document origin ranking
        question: obvious
        
        Note: uncomment 
    """
    passages_tuple = map(lambda x: (x[0].lower(), x[1]), passages_tuple)
    dictionary = dict(passages_tuple)
    #print (passages_tuple)
    passages, passage_rankings = zip(*passages_tuple)
    
    question, keywords = question.lower(), map(str.lower, keywords)
    
    rankings = zip(#NE_rank(question, passages),
                   num_keywords_rank(' '.join(keywords), passages),
                   exact_sequence_rank(question, passages),
                   # Document rank has not been tested yet
                   document_rank(dictionary, passages),
                   findAllProximities(keywords, passages),
                   getNGramOverlap(question, passages, 1),
                   getNGramOverlap(question, passages, 2),
                   getNGramOverlap(question, passages, 3),
                   checkClassConsistency(question,passages))
    # Shortened weights while NE_rank is too slow
    return sorted(zip ( map(lambda x: dot(x,WEIGHTS), rankings), passages), key = lambda t: -t[0])


# This is for testing purposes
def passage_rankings(question, passages_tuple, keywords):
    """
        WORLDS WRST FUNCTON EVR
        passages: list of passages
        passage_rankings: passage --> document origin ranking
        question: obvious
        
        Note: uncomment 
    """
    passages_tuple = map(lambda x: (x[0].lower(), x[1]), passages_tuple)
    dictionary = dict(passages_tuple)
    passages, passage_rankings = zip(*passages_tuple)
    
    question, keywords = question.lower(), map(str.lower, keywords)
    
    rankings = zip(#NE_rank(question, passages),
                   num_keywords_rank(' '.join(keywords), passages),
                   exact_sequence_rank(question, passages),
                   # Document rank has not been tested yet
                   document_rank(dictionary, passages),
                   findAllProximities(keywords, passages),
                   getNGramOverlap(question, passages, 1),
                   getNGramOverlap(question, passages, 2),
                   getNGramOverlap(question, passages, 3))
    # Shortened weights while NE_rank is too slow
    return rankings

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
    # Constants for score. A larger top will put more weight on the number
    # of overlapping words. A larger bottom will put more weight on the distance
    top = 1.0
    bottom = 1.0
    for p in passages:
        (numWords, totalDistance, allDistances) = findProximity(keywords, p)
        if totalDistance != 0:
            proximityList.append((numWords*top) / (totalDistance*bottom))
        else:
            proximityList.append(0.0)
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
            tagString = ' '.join(tagSeq)
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
        count = len(filter(lambda x: x in questionDict, grams))
        overlapList.append(count)
    return overlapList

QWORD_DICT = {"how":lambda s: re.search("\d",s),
			  "when":lambda s: re.search("\d",s),
			  "name":lambda s: s[0] == s[0].upper(),
			  "who":lambda s: s[0] == s[0].upper()}
    
def checkClassConsistency(question,passages):
    '''
    Input: the question and a list of passages
    Output: a binary list where 1 means the passage matches the class 
    style (i.e. has a number, has a name, etc)
    '''
    for qword in QWORD_DICT:
        if qword in question:
            break
    return map(lambda p: 1 if QWORD_DICT[qword](p) else 0,passages)
        
