#!/usr/bin/env python

##  extend_previously_trained_tokenizer.py

"""
You need this script if, after you have trained a tokenizer, you wish you had trained it for
larger token vocabulary size.  This script allows you to simply augment the tokenizer you currently
have with additional training.  The alternative would be to start from scratch, but that can be
frustrating since tokenizer training is CPU intensive and can take a long time.

Example call syntax:

    python3  extend_previously_trained_tokenizer.py   111_babygpt_tokenizer_49700.json   60000 
                                                      ^^^                   ^^^^^

This call syntax means that '111_babygpt_tokenizer_49700.json' is the tokenizer JSON for what you
got with previous training that was based on a target token vocab of 50000.  But now, with 
additional training, you want to increase the token vocab size to 60000.

This function can only be used with the tokenizers created with Versions 1.0.9 or greater of 
babyGPT.
"""

from babyGPT import *


#articles_dir = '/mnt/cloudNAS3/Avi/TextDatasets/datasets_for_babyGPT/saved_articles_dir_12M'
#articles_dir = '/home/kak/TextDatasets/datasets_for_babyGPT/saved_articles_dir_12M'
#articles_dir = '/home/kak/TextDatasets/datasets_for_babyGPT/saved_Adrien_News_Articles_56M'
articles_dir = '/mnt/cloudNAS3/Avi/TextDatasets/datasets_for_babyGPT/saved_Adrien_News_Articles_56M'


if len(sys.argv) != 3:  
    sys.stderr.write("Usage: %s   <tokenizer_json>  <new_size_for_token_vocab>\n" % sys.argv[0])   
    sys.exit(1)  

tokenizer_json = sys.argv[1]
new_size_for_token_vocab = int(sys.argv[2])

tokenizer_trainer = babyGPT.TrainTokenizer( 
                        corpus_directory = articles_dir,
                        target_vocab_size=new_size_for_token_vocab, 
                    )                    

tokenizer_trainer.extend_tokenizer_with_additional_training( tokenizer_json )

