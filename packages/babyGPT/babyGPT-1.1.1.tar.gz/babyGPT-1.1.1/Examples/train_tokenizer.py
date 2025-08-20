#!/usr/bin/env python

##  train_tokenizer.py

"""
IMPORTANT IMPORTANT IMPORTANT IMPORTANT IMPORTANT:

   The tokenizer automatically constructs a filename for the tokenizer JSON.  This 
   filename will look like
                      
              109_babygpt_tokenizer_50000.json

   where "104" stands for the Version 1.0.9 of the babyGPT module.   The number 
   60000 in the name of the JSON file is for the vocabulary size of the tokenizer.


                     --------------------------  

About the script in this file:

If the text corpus you have collected is for a specialized domain (such as
movies, sports, healthcare, etc.), you are likely to get better results from babyGPT
if you first train a tokenizer for that domain.  For training a new tokenizer, all
you have to do is invoke this script with

               python3 train_tokenizer.py

after you have set the "articles_dir" in the code as shown below.  Regarding the 
directory that the "articles_dir" variable currently points to

                    saved_Adrien_News_Articles_56M

that corpus was created by Adrien Dubois.  See the README_by_Adrien in the directory
for further information regarding the corpus.  As mentioned in that document, that
text corpus is about athlete news.
"""

from babyGPT import *

#articles_dir = '/mnt/cloudNAS3/Avi/TextDatasets/datasets_for_babyGPT/saved_articles_dir_12M'
#articles_dir = '/home/kak/TextDatasets/datasets_for_babyGPT/saved_articles_dir_12M'
#articles_dir = '/home/kak/TextDatasets/datasets_for_babyGPT/saved_Adrien_News_Articles_56M'
articles_dir = '/mnt/cloudNAS3/Avi/TextDatasets/datasets_for_babyGPT/saved_Adrien_News_Articles_56M'

tokenizer_trainer = babyGPT.TrainTokenizer( 
                        corpus_directory = articles_dir,
                        target_vocab_size=50000, 
                    )                    

merge_rules_dict, merges = tokenizer_trainer.train_tokenizer()        ## basic tokenizer training

tokenizer_trainer.post_training_cleanup()                             ## post-training cleanup

