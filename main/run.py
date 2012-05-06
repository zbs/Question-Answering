#! /usr/bin/python

from Question import Question
import BuildQuery
import re 

IS_TEST = False
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

def extract_answers(answers_file):
    # key: question number
    # value: list of answer texts
    answers = {}
    answer_in = -1
    for line in open(answers_file):
        answer_in -= 1
        if line.startswith("Question"):
            answer_in = 3
            qNumber = int(line.split()[-1])
            answers[qNumber] = []
        elif line.startswith("\n"):
            answer_in = -1
        elif not answer_in:
            answers[qNumber].append(line[:-1])
            answer_in = 1
    return answers

def MRR():
    answers = extract_answers(answers_file)
    fp = open(output_file, 'r')
    output = fp.read().split('\n')
    sum_ = 0.
    for index, key in enumerate(answers):
        q_answers = output[index * 5: index*6 + 4]
        for rank, q_answer in enumerate(q_answers):
#            cur_answer = answers[key]
#            if q_answer.find(cur_answer) != -1:
            if filter(lambda x: q_answer.find(x) != -1, answers[key]):
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
    output = open(output_file,"w")
    for qNumber in questions:
        print "\n"
        docs = DOCS + "top_docs." + str(qNumber) + ".gz"
        #print questions[qNumber]
        question = Question(qNumber,questions[qNumber],docs)
        # Can do baseline here or do full process.
        # Get expanded question:
        query = BuildQuery.buildFullQuery(questions[qNumber], hyponyms=False, hypernyms=False)
        print query
        ir_results = question.search(query)
        #print ir_results
        passages = question.golden_passage_retriever(ir_results)
        top5 = question.top5(passages)
        for answer in top5:
            print answer
            output.write(str(qNumber) + " top_docs." + str(qNumber) + " " + answer + "\n")
    output.close()
    if not IS_TEST:
        score = MRR()
        print score
    print "done"

def justDoIR():
    questions = extract_questions(questions_file)
    output = open("../IRoutput.txt", 'w')
    for qNumber in questions:
        docs = DOCS + "top_docs." + str(qNumber) + ".gz"
        question = Question(qNumber,questions[qNumber],docs)
        # Can do baseline here or do full process.
        # Get expanded question:
        query = questions[qNumber]
        query = BuildQuery.buildFullQuery(query, hyponyms=False, hypernyms=False)
        ir_results = question.search(query)
        for (_,answer) in ir_results:
            output.write(answer+"\n")
    output.close()


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
    f = open("../IRoutput.txt")
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
            print "Qid is "+qID
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

def analyzeClasses():
    questions = extract_questions(questions_file)
    answers = extract_answers(answers_file)
    qwordsDict = {"how":[],"when":[],"who":[],"name":[]}
    for id in answers:
        if "how" in questions[id].lower():
            for answer in answers[id]:
                if re.search("\d",answer):
                    qwordsDict["how"] += [1]
                else:
                    qwordsDict["how"] += [0]
        if "who" in questions[id].lower():
            for answer in answers[id]:
                if answer[0] == answer[0].upper():
                    qwordsDict["who"] += [1]
                else:
                    qwordsDict["who"] += [0]
        if "name" in questions[id].lower():
            for answer in answers[id]:
                if answer[0] == answer[0].upper():
                    qwordsDict["name"] += [1]
                else:
                    qwordsDict["name"] += [0]
        if "when" in questions[id].lower():
            for answer in answers[id]:
                if re.search("\d",answer):
                    qwordsDict["when"] += [1]
                else:
                    qwordsDict["when"] += [0]
    for q in qwordsDict:
        list = qwordsDict[q]
        print q, (float(sum(list))/float(len(list)))

if __name__ == '__main__':
    #main()
    print MRR()
