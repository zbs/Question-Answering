#! /usr/bin/python

from Question import Question
from BuildQuery import buildFullQuery

question = 'Where is Belize located?'
number = 202
def run_for_question(question, number):
    q = Question(number, question, '../docs/top_docs.%d.gz'%number)
    query = buildQuery(question)
    
    documents = q.search(query)
    rankings = q.golden_passage_retriever(documents)
    passage_metrics = q.test(rankings)
    
    return map(lambda x: float(sum(x)) / len(x), zip(*passage_metrics))

<<<<<<< HEAD
q = Question(number, question, '../docs/top_docs.%d.gz'%number)
query = buildFullQuery(question, hyponyms=False, hypernyms=False)

documents = q.search(query)
rankings = q.golden_passage_retriever(documents)
passage_metrics = q.test(rankings)

print str(map(lambda x: float(sum(x)) / len(x), zip(*passage_metrics)))
=======
print str(run_for_question(question, number))
>>>>>>> 96612d8ae53ab4c03da0eb6cd2becde544da23ae
