#! /usr/bin/python

#from Question import Question
import BuildQuery, Question
import re 

questions_file = "../questions.txt"
answers_file = "../answers.txt"
DOCS = "../docs/"
output_file = "../output.txt"

# extracts data from questions file...
def extract_questions(questions_file):
    # key: question number
    # value: question text
    questions = {}
    isText = False
    qNumber = 0
    qText = ""
    for line in open(questions_file):
        if line.startswith("</top>"):
            questions[qNumber] = qText
            qNumber = 0
            qText = ""
        elif line.startswith("<num>"):
            qNumber = int(line.split()[-1])
        elif line.startswith("<desc>"):
            isText = True
        elif isText:
            qText = line[:-1]
            isText = False
    return questions

def extract_answers(answers_file, answer_line_no=4):
    with open(answers_file, 'r') as fp:
        answer_text = fp.read()

    answers = {}
    answer_chunks = filter(bool, map(str.strip, answer_text.split('\n\n')))
    for chunk in answer_chunks:
        chunk_lines = map(str.strip, chunk.split('\n'))
        question_no = re.match('^Question (?P<number>[0-9]+)$', \
                               chunk_lines[0]).group('number')    
        answers[int(question_no)] = chunk_lines[answer_line_no-1]
    return answers
    
def extract_documents(filename):
    with open(filename) as fp:
        text = fp.read()
    return text.split('\n\n')

def MRR(answers_file, output_file):
    answers = extract_answers(answers_file)
    with open(output_file, 'r') as fp:
        output = fp.read().split('\n')
    sum_ = 0.
    for index, key in enumerate(answers):
        q_answers = output[index * 5: index*6 + 4]
        for rank, q_answer in enumerate(q_answers):
            cur_answer = answers[key]
            if q_answer.find(cur_answer) != -1:
                sum_ += 1./float((rank+1))
                break
    return sum_ / float(len(answers))
    

def MRR_(answers_file, output_file):
    """
    Computes the Mean Reciprocal Rank of the output_file
    """
    answers = extract_answers(answers_file)
    currentQuestion = -1
    lastQuestionAnswered = -1
    numQuestions = 0
    currentRank = 1
    score = 0.0
    
    output = open(output_file)
    for line in output.readlines():
        pieces = line.split(" ")
        qNumber = int(pieces[0])
        document = pieces[1]
        guess = " ".join(pieces[2:])
        
        #reset rank if this is a new qNumber
        #also increment the number of questions
        if currentQuestion != qNumber:
            currentQuestion = qNumber
            currentRank = 1
            numQuestions += 1
        
        #skip over this line if this qNumber has already been answered
        if lastQuestionAnswered == qNumber:
            continue
        
        #add 1/rank to the score if guess contains the answer
        if answers[qNumber].lower() in guess.lower():
            print "got one!"
            print qNumber
            print answers[qNumber].lower()
            print guess.lower()
            score += 1.0/currentRank
            lastQuestionAnswered = qNumber
        
        #increment rank
        currentRank += 1
    return score/numQuestions

def main():
    questions = extract_questions(questions_file)
    answers = extract_answers(answers_file)
    score = 0.0
    output = open(output_file,"w")
    allDocs = []
    for qNumber in questions:
        docs = DOCS + "top_docs." + str(qNumber) + ".gz"
        question = Question(qNumber,questions[qNumber],docs)
        # Can do baseline here or do full process.
        # Get expanded question:
        query = questions[qNumber]
        synset = BuildQuery.buildSynset(query, hyponyms=True, hypernyms=False)
        synset = BuildQuery.trimSynset(query, synset)
        query += " ".join(synset)
        documents = question.search(query)
        for (tup, d) in documents:
            output.write(d)
        allDocs.append(documents)
        """
        guesses = question.run_baseline()
        for (_,doc,guess) in guesses:
            if not doc or not guess:
                doc = "nil"
                guess = "nil"
            output.write(str(qNumber) + " " + doc + " " + guess + "\n")
            print (str(qNumber) + " " + doc + " " + guess)
        """
    output.close()
    #mrr = MRR(answers_file, output_file) Errors in MRR? not working.
    #print "MRR: " + str(mrr)
    return allDocs
    '''
        if answers[qNumber].lower() in guess.lower():
            score +=1
            print "got one!"
            print qNumber
            print answers[qNumber].lower()
            print guess.lower()
    accuracy = score / len(questions)
    print "Correct Guesses: " + str(score)
    print "Accuracy: " + str(accuracy)
    '''

def checkIR():
    """ Returns proportion of search results that contain the document
    with the answer according to answers.txt """
    f = open("../answers.txt")
    answers = f.readlines()
    f.close()
    answerDocs = []
    # Get correct docs from answer
    for i in range(len(answers)):
        if answers[i][0:8] == "Question":
            i += 2
            correctDoc = answers[i].rstrip('\n')
            answerDocs.append(correctDoc)
    # Check how many questions have the correct document returned
    f = open("../output.txt")
    output = f.readlines()
    f.close()
    currentDoc = ""
    currentAnswer = ""
    numCorrect = 0
    numDocs = 0
    answersAppear = range(201, 400)
    for i in range(len(output)):
        if "Qid" in output[i][0:9]:
            numDocs += 1
            qID = output[i].split("\t")[0].split(" ")[1]
            if qID != currentDoc:
                currentDoc = qID
                if int(qID) in answersAppear:
                    answersAppear.remove(int(qID))
            i += 2
            #print "output is: "
            #print output[i]
            if "</DOCNO>" in output[i]:
                try:
                    docID = output[i].split(">")[1].split("<")[0].strip(" ")
                    #print docID
                except IndexError:
                    print output[i]
            if docID in answerDocs:
                numCorrect += 1
    print "There are %d documents in output and %d answerDocs" %(numDocs, len(answerDocs))
    # How many questions actually have documents returned for them? Hopefully all.
    # If so, list should be empty.
    print answersAppear
    return float(numCorrect) / len(answerDocs)

if __name__ == '__main__':
    #main()
    print "check"
    answers = extract_answers(answers_file)
    for i in answers:
        print answers[i]
