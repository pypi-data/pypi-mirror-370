#!/usr/bin/env python

##  interact_with_prompts.py

"""
    IMPORTANT IMPORTANT IMPORTANT:

           The transformer configuration parameters in this script MUST be
           exactly the same as in the script

                     create_base_model_with_buffered_context.py

           Thee parameters are:

                 max_seq_length
                 context_window_size
                 context_buffer_size
                 batch_size
                 embedding_size
                 num_basic_decoders 
                 num_atten_heads
                 num_atten_heads

           In addition, you must use the same tokenizer JSON file.

         --------------------------------------------------------------
   
    Doc for this script:

    This is the script for interacting with a trained babyGPT model through prompts.
    The idea is that you supply a small number of words (as, say, the beginning of a
    new thought) as a prompt and the model supplies the rest of the words to complete
    the thought.  At this time, the model extends your prompt until it reaches a
    period (or the end dictated by the size of the "max_seq_length" parameter.

    Any interaction with a trained GPT model has to deal with the following issue:
    What to do with the context buffer that is meant to be a continuation of the last
    part of the previous "sentence" fed into the transformer.

    Ideally, we should be placing in the context buffer words that create a context
    for the prompt.  But there is no easy way to that without a more elaborate
    model. An example of more elaborate modeling would be to have the input to the
    transformer consist of, say, an SOS token, a special context token consisting
    possibly of integer index values beyond the tokenizer vocab, followed by a
    context buffer that would be the last part of the previous sentence, followed,
    finally, by the new input tokens.

    babyGPT gives you two options regarding what to do with the context buffer for
    your prompt:

            --  all_zeros

            --  get_from_prompt

    With the first option, all of the integer encoding values in the context buffer
    are set to the integer zero.  And, with the second option, at this time, the
    context buffer contains a portion or all of the prompt itself.  If the tokenized
    version of the prompt is shorter than the size of the context buffer, only the
    context_buffer_size number of elements of the prompt are retained for the context
    buffer.  In the opposite case, just the initial context_buffer_size number of
    elements of the prompt are retained.
"""


import random
import numpy
import torch
import os, sys

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

from babyGPT import *

tokenizer_json  =  '104_babygpt_tokenizer_49270.json'

max_seq_length = 55
context_window_size = 50
context_buffer_size = 5

assert context_window_size + context_buffer_size == max_seq_length,  "context_window_size plus context_buffer_size must add up to max_seq_length"

batch_size = 50
embedding_size = 384
#num_basic_decoders = num_atten_heads = 4     

num_basic_decoders = 6
num_atten_heads = 8     

optimizer_params = {'beta1' : 0.9,  'beta2': 0.98,  'epsilon' : 1e-6}

num_warmup_steps = 4000

masking = True         

baby_gpt = babyGPT(
                    max_seq_length = max_seq_length,
                    batch_size = batch_size,
                    embedding_size = embedding_size,
                    num_basic_decoders = num_basic_decoders,
                    num_atten_heads = num_atten_heads,
                    optimizer_params = {'beta1' : 0.9,  'beta2': 0.98,  'epsilon' : 1e-6},
                    num_warmup_steps = num_warmup_steps,
                    masking = masking,
                    use_gpu = True,
                    verify_text_corpus = False,
                    path_saved_model = {"decoder" : "saved_decoder",                                                             
                                        "embedding_generator" : "saved_embedding_generator",                             
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

prompt_responder = baby_gpt.PromptResponder(
                       baby_gpt,
                       xformer,
                       master_decoder,
                       context_window_size = context_window_size,
                       context_buffer_size = context_buffer_size,
                       tokenizer_json = tokenizer_json,                       
                       checkpoint_dir = "checkpoint_dir",
                       checkpoint_index = 36000,                      ## <<<<< Do not forget to indicate which checkpoint to use
                   )


prompt_responder.generate_response_to_prompt_up_to_period(context_buffer_option = "all_zeros")

#prompt_responder.generate_response_to_prompt_up_to_period(context_buffer_option = "get_from_prompt")


