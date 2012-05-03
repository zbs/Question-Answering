'''
Created on Apr 30, 2012

@author: zach
'''
import unittest
import main.Ranker as Ranker

class Test(unittest.TestCase):

    def testNumKeywordsRank(self):
        question = "What was the name of the first silent movie ?"
        passages = ["Movies are great", 'I love silent nights', \
                    'No name eludes me', 'The name of your mother',
                    'The first silent movie is not known to me']
        expected_rankings = [0, 1, 1, 3, 4]
        self.assertEquals(expected_rankings, Ranker.num_keywords_rank(question, passages))
    
    def testExactSequenceRank(self):
        question = "How many toes are there on the hoof of a buffalo ?"
        passages = ['how many toes', 'are there on', 'on the hoof of a buffalo baby',
                    'how many times have I told you that there are no toes on the hoof of a buffalo ?']

        expected_rankings = [3, 3, 6, 7]
        self.assertEquals(expected_rankings, Ranker.exact_sequence_rank(question, passages))
    
    def testNERank(self):
        question = 'Who was Charles Lindbergh and where was he born ?'
        print Ranker.ne_extract(question)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()