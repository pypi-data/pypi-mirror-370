#!/usr/bin/env python

##  create_base_model_with_buffered_context.py


"""
This is the script to run if you want to create a Base Model for your corpus.  By
Base Model I mean a language model acquired through unsupervised learning.


This script assumes:


    1)   You have created a corpus by running the script 

                      run_gatherer.py

         Or:

         You are using one of the two corpora that you can download from the
         Purdue University page for this module.  These are available through
         the link

                      "Download the text datasets for babyGPT"


    2)   If the corpus is for a specialized domain (for, say, the medical domain), 
         you have trained a tokenizer for the corpus by running the script 

                      train_tokenizer.py



After you have created the Base Model, you can test its quality by executing the
the script

                      interact_with_prompts.py


Call syntax for this script:


                      python3   create_base_model_with_buffered_context.py


but first make sure that the corpus directory is set correctly and so is the JSON 
file for the tokenizer


                     ==========================================


HOW TO CHOOSE THE PARAMETERS:

If your GPU memory is around 10GB, you're going to be limited to the following
parameters:

    max_seq_length        =   30
    context_window_size   =   25
    context_buffer_size   =   5
    batch_size            =   50
    embedding_size        =   128

On the other hand, if your GPU memory is around 24 GB, you should be able to 
use the following values for the parameters:

    max_seq_length        =   55
    context_window_size   =   50
    context_buffer_size   =   5
    batch_size            =   50
    embedding_size        =   384

The above choices are based on the following parameters choices for the transformer:

   num_basic_decoders = 4              [Number of transformer stages]
   num_atten_heads = 8                 [Number of attention heads in each stage]

"""

import random
import numpy
import torch
import os, sys
import lightning as L

"""
seed = 0           
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
numpy.random.seed(seed)
torch.backends.cudnn.deterministic=True
torch.backends.cudnn.benchmarks=False
os.environ['PYTHONHASHSEED'] = str(seed)
"""

##  watch -d -n 0.5 nvidia-smi
##  tensorboard --logdir=lightning_logs/

from babyGPT import *

#articles_dir = '/home/kak/TextDatasets/datasets_for_babyGPT/saved_Adrien_News_Articles_56M'
articles_dir = '/mnt/cloudNAS3/Avi/TextDatasets/babyGPT_datasets/saved_Adrien_News_Articles_56M'
#articles_dir = '/mnt/cloudNAS3/Avi/TextDatasets/babyGPT_datasets/saved_articles_dir_12M'


##  This tokenizer was trained with the 'saved_Adrien_News_Articles_56M' corpus of athlete news articles:
tokenizer_json  =  '109_babygpt_tokenizer_49275.json'

#   The following tokenizer was trained with the smaller dataset "saved_articles_dir_12M"
#tokenizer_json  =  'simple_toke_50000.json'

##  IMPORTANT:   If your hardware allows, set max_seq_length to as large a value as you can, preferably 128

#max_seq_length = 30
max_seq_length = 55

##  IMPORTANT:   If are able to set max_seq_length to 128, set context_window_size to 110
#context_window_size = 25
context_window_size = 50

##  IMPORTANT:   This is always the difference between max_seq_length and context_window_size
context_buffer_size = 5

assert context_window_size + context_buffer_size == max_seq_length,  "context_window_size plus context_buffer_size must add up to max_seq_length"

##  IMPORTANT:   Make your batch_size as large as allowed by hardware constraints
batch_size = 50
#batch_size = 20

##  IMPORTANT:   Given a large enough GPU (in terms of its memory), I'd set embedding_size to 256 or even 512
#embedding_size = 256
embedding_size = 384
#embedding_size = 512

#num_basic_decoders = num_atten_heads = 4     

num_basic_decoders = 6
num_atten_heads = 8

if ( (embedding_size // num_atten_heads) * num_atten_heads != embedding_size ):
    sys.exit("\n\nAboring! The number of attention heads must be an integral divisor of the embedding size\n\n")

optimizer_params = {'beta1' : 0.9,  'beta2': 0.98,  'epsilon' : 1e-6}
num_warmup_steps = 4000

masking = True         

baby_gpt = babyGPT(
                    max_seq_length = max_seq_length,
                    batch_size = batch_size,
                    embedding_size = embedding_size,
                    num_basic_decoders = num_basic_decoders,
                    num_atten_heads = num_atten_heads,
                    optimizer_params = optimizer_params,
                    num_warmup_steps = num_warmup_steps,
                    masking = masking,
                    verify_text_corpus = False,
                    path_saved_model = {"decoder" : "./saved_decoder",  
                                        "embedding_generator" : "./saved_embedding_generator",   
                                       },
                  )

xformer = baby_gpt.TransformerFG( 
                    max_seq_length = max_seq_length,
                    embedding_size = embedding_size,
                    tokenizer_json = tokenizer_json,
                    num_warmup_steps = num_warmup_steps,
                    optimizer_params = optimizer_params,
          )

master_decoder = baby_gpt.MasterDecoderWithMasking(
                    xformer, 
                    num_basic_decoders = num_basic_decoders,
                    num_atten_heads = num_atten_heads,
                    context_window_size = context_window_size,
                    context_buffer_size = context_buffer_size,
                    batch_size = batch_size,
                    masking = masking
                 )

dataloader = baby_gpt.ArticleDatasetWithBufferedContext(
                    gpt = baby_gpt,
                    tokenizer_json = tokenizer_json,
                    context_window_size = context_window_size,
                    context_buffer_size = context_buffer_size,
                    articles_dir = articles_dir,
             )

number_of_learnable_params_in_decoder = sum(p.numel() for p in master_decoder.parameters() if p.requires_grad)
print("\n\nThe number of learnable parameters in the Master Decoder: %d" % number_of_learnable_params_in_decoder)

print("""\n\n\nIf your training corpus is several megabytes in size (say over 100MB), it may take a few
         minutes to set up the token streams for the individual batch instances.  

                               PLEASE BE PATIENT\n""")

baby_gpt.run_code_with_buffered_context_for_training_TransformerFG(xformer, master_decoder, dataloader, checkpoint_frequency = 4000)


