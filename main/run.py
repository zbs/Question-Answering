#! /usr/bin/python

from Question import Question
import BuildQuery

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
    # value: answer text
    answers = {}
    answer_in = -1
    for line in open(answers_file):
        answer_in -= 1
        if line.startswith("Question"):
            answer_in = 3
            qNumber = int(line.split()[-1])
        elif not answer_in:
            answers[qNumber] = line[:-1]
    return answers

def extract_documents(filename):
    with open(filename) as fp:
        text = fp.read()
    return text.split('\n\n')

def MRR(answers_file, output_file):
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
        print len(documents)
        print documents[1]
        return documents
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
    mrr = MRR(answers_file, output_file)
    print "MRR: " + str(mrr)
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

if __name__ == '__main__':
    main()
