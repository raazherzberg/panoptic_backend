# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 12:08:07 2017

@author: Gilad
"""

import urllib
from json import JSONDecoder
#from nltk.stem import PorterStemmer
import re

sources = ["the-new-york-times","bbc-news","cnn","the-wall-street-journal","breitbart-news"]
key = "f73616ed90dd4e0c8a9a81a05f04a575"

first = "https://newsapi.org/v1/articles?source="
second = "&sortBy=top&apiKey="

stopwords = set([u'i',
 u'me',
 u'my',
 u'myself',
 u'we',
 u'our',
 u'ours',
 u'ourselves',
 u'you',
 u'your',
 u'yours',
 u'yourself',
 u'yourselves',
 u'he',
 u'him',
 u'his',
 u'himself',
 u'she',
 u'her',
 u'hers',
 u'herself',
 u'it',
 u'its',
 u'itself',
 u'they',
 u'them',
 u'their',
 u'theirs',
 u'themselves',
 u'what',
 u'which',
 u'who',
 u'whom',
 u'this',
 u'that',
 u'these',
 u'those',
 u'am',
 u'is',
 u'are',
 u'was',
 u'were',
 u'be',
 u'been',
 u'being',
 u'have',
 u'has',
 u'had',
 u'having',
 u'do',
 u'does',
 u'did',
 u'doing',
 u'a',
 u'an',
 u'the',
 u'and',
 u'but',
 u'if',
 u'or',
 u'because',
 u'as',
 u'until',
 u'while',
 u'of',
 u'at',
 u'by',
 u'for',
 u'with',
 u'about',
 u'against',
 u'between',
 u'into',
 u'through',
 u'during',
 u'before',
 u'after',
 u'above',
 u'below',
 u'to',
 u'from',
 u'up',
 u'down',
 u'in',
 u'out',
 u'on',
 u'off',
 u'over',
 u'under',
 u'again',
 u'further',
 u'then',
 u'once',
 u'here',
 u'there',
 u'when',
 u'where',
 u'why',
 u'how',
 u'all',
 u'any',
 u'both',
 u'each',
 u'few',
 u'more',
 u'most',
 u'other',
 u'some',
 u'such',
 u'no',
 u'nor',
 u'not',
 u'only',
 u'own',
 u'same',
 u'so',
 u'than',
 u'too',
 u'very',
 u's',
 u't',
 u'can',
 u'will',
 u'just',
 u'don',
 u'should',
 u'now',
 u'd',
 u'll',
 u'm',
 u'o',
 u're',
 u've',
 u'y',
 u'ain',
 u'aren',
 u'couldn',
 u'didn',
 u'doesn',
 u'hadn',
 u'hasn',
 u'haven',
 u'isn',
 u'ma',
 u'mightn',
 u'mustn',
 u'needn',
 u'shan',
 u'shouldn',
 u'wasn',
 u'weren',
 u'won',
 u'wouldn'])

class Article:
    def __init__(self, title, url, img, source):
        self.title = title
        self.url = url
        self.img = img
        self.source = source
        
class DumbStemmer:
    def stem(self,word):
        return word
        

def collect():
    articles = []
    decoder = JSONDecoder()
    
    for source in sources:
        text = urllib.urlopen(first + source + second + key).readline()
        elements = decoder.decode(text)["articles"]
        for element in elements:
            title = element["title"]
            url = element["url"]
            img = element["urlToImage"]
            articles.append(Article(title,url,img,source))
    
    return articles

def lambda_handler(event, context):
    articles = collect()
    titles = [article.title for article in articles]
    #stemmer = PorterStemmer()
    #stop = set([stemmer.stem(word) for word in stopwords.words('english')])
    
    #tokenized = [set([stemmer.stem(word.lower()) for word in re.split('[^a-zA-Z0-9]', title) if  word not in stop]) for title in titles]
    tokenized = [set([word.lower() for word in re.split('[^a-zA-Z0-9]', title) if  word not in stopwords]) for title in titles]
    scores = []
    
    for i in range(len(titles)):
        for j in range(i + 1,len(titles)):
            a1 = articles[i]
            a2 = articles[j]
            if a1.source != a2.source:
                e1 = tokenized[i]
                e2 = tokenized[j]
                score = float(len(e1.intersection(e2))) / len(e1.union(e2))
                
                scores.append((a1, a2, score))
    
    limited = [elem for elem in scores if elem[2] > 0.2]
    limited = sorted(limited, reverse=True, key=lambda x: x[2])
    clusters = []
    
    while limited:
        elem = limited.pop(0)
        sources = set([elem[0].source,elem[1].source])
        toAdd = [elem[0],elem[1]]
        added = []
        for score in limited:
            if score[0] in toAdd:
                if score[1].source not in sources:
                    toAdd.append(score[1])
                    added.append(score)
                    sources.add(score[1].source)
            elif score[1] in toAdd:
                if score[0].source not in sources:
                    toAdd.append(score[0])
                    added.append(score)
                    sources.add(score[0].source)
        #clusters.append([article.title for article in toAdd])
        clusters.append([article.__dict__ for article in toAdd])
        for score in added:
            limited.remove(score)
        
    return clusters