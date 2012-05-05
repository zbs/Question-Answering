'''
Created on May 1, 2012

@author: Benjamin Jaeger
'''
import re
import nltk as n
TYPES = {
        'ENTY:animal': 2, 'NUM:date': 8, 'ENTY:event': 10, 'ENTY:dismed': 24, 'ABBR:abb': 36, 'ENTY:product': 27, 'LOC:mount': 25,
        'ENTY:body': 23, 'ENTY:techmeth': 32, 'ENTY:instru': 35, 'NUM:ord': 46, 'LOC:city': 22, 'ENTY:color': 20, 'ENTY:food': 18,
        'LOC:other': 16, 'NUM:dist': 43, 'ENTY:plant': 31, 'ENTY:termeq': 21, 'NUM:perc': 41, 'NUM:code': 42, 'LOC:state': 11,
        'ABBR:exp': 3, 'HUM:gr': 5, 'ENTY:word': 39, 'DESC:reason': 9, 'ENTY:symbol': 45, 'HUM:desc': 34, 'ENTY:letter': 15,
        'NUM:period': 28, 'NUM:other': 37, 'ENTY:other': 14, 'ENTY:cremat': 1, 'ENTY:veh': 47, 'NUM:count': 13, 'LOC:country': 19,
        'ENTY:religion': 17, 'DESC:manner': 0, 'HUM:ind': 4, 'NUM:speed': 38, 'ENTY:sport': 30, 'ENTY:substance': 29,
        'ENTY:lang': 40, 'NUM:temp': 44, 'DESC:desc': 12, 'DESC:def': 7, 'NUM:money': 26, 'NUM:volsize': 33, 'HUM:title': 6}

WH_WORDS = {'what':0 , 'which':1, 'when':2, 'where':3, 'who':4, 'how':5, 'why':6, 'other':7}

def parse(filename):
    X,Y = [], []
    for line in open(filename):
        question_pair = line.split(" ", 1)
        X.append(question_pair[0])
        Y.append( TYPES[ question_pair[1] ])
    return X,Y
    
        
def find_wh(question):
    for wh in WH_WORDS.iterkeys():
        if re.search(wh, question):
            return WH_WORDS[wh]
    return WH_WORDS['other']

def find_head_word(question):
    pass

#1,2,3-grams
def find_ngrams(question):
    pass

#parse("../train_1000.label.txt")
n.ne_chunk( n.pos_tag(n.word_tokenize("He walked the dog")))
