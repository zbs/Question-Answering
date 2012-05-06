#! /usr/bin/python

from Question import Question
<<<<<<< HEAD
import BuildQuery
=======
from BuildQuery import buildFullQuery
>>>>>>> f5194df0fabd3c7bdf0cac3fee492bb716af177b

question = 'Where is Belize located?'
number = 202
def run_for_question(question, number):
    q = Question(number, question, '../docs/top_docs.%d.gz'%number)
    query = BuildQuery.buildQuery(question)
    
    documents = q.search(query)
    rankings = q.golden_passage_retriever(documents)
    passage_metrics = q.test(rankings)
    
    return map(lambda x: float(sum(x)) / len(x), zip(*passage_metrics))

questions = BuildQuery.getQuestions()
ranking_list = []
base = 201
for i in range(0,15):
    ranking_list.append(run_for_question(questions[i][1], questions[i][0]))

avg = map(lambda x: float(sum(x)) / len(x), zip(*ranking_list))
print avg
