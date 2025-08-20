#!/usr/bin/env python

##  run_gatherer.py

"""
This script is for collecting a corpus of news articles for experimenting with
babyGPT.  The script requires a list of URLs as article sources. These are supplied
through the variable 'urls' as shown by the following example:

    urls = ['https://finance.yahoo.com','http://cnn.com',
             'https://purdueexponent.org','https://slate.com',
             'https://sports.yahoo.com',
             'https://timesofindia.indiatimes.com',
             'http://cnn.com',
             'https://slate.com'
           ]

Calling syntax:

               python3 run_gatherer.py
"""

from babyGPT import *

urls = ['https://finance.yahoo.com',
        'https://purdueexponent.org',
        'https://sports.yahoo.com',
        'https://timesofindia.indiatimes.com',
        'http://cnn.com',
        'https://slate.com'
       ]

articles_dir = 'saved_April_12_articles_dir'

baby_gpt = babyGPT(
                    urls  =  urls,
                  )

gatherer = baby_gpt.ArticleGatherer(
                    baby_gpt, 
                    urls = urls, 
                    articles_dir = articles_dir,
           )

gatherer.download_articles()

