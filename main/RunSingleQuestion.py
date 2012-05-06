#! /usr/bin/python

from Question import Question
from BuildQuery import buildQuery

question = 'Where is Belize located?'
number = 202

q = Question(number, question, '../docs/top_docs.%d.gz'%number)
query = buildQuery(question)

documents = q.search(query)
rankings = q.golden_passage_retriever(documents)
passage_metrics = q.test(rankings)

print str(map(lambda x: float(sum(x)) / len(x), zip(*passage_metrics)))
