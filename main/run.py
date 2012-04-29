from Question import Question

questions_file = "../questions.txt"
answers_file = "../answers.txt"
DOCS = "../docs/"

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
    return text.split('\n')
    
def main():
    questions = extract_questions(questions_file)
    answers = extract_answers(answers_file)
    score = 0.0
    for qNumber in questions:
        docs = DOCS + "top_docs." + str(qNumber) + ".gz"
        question = Question(qNumber,questions[qNumber],docs)
        guess = question.run_baseline()
        if answers[qNumber].lower() in guess.lower():
            score +=1
            print "got one!"
            print qNumber
            print answers[qNumber].lower()
            print guess.lower()
    accuracy = score / len(questions)
    print "Correct Guesses: " + str(score)
    print "Accuracy: " + str(accuracy)

if __name__ == '__main__':
    main()