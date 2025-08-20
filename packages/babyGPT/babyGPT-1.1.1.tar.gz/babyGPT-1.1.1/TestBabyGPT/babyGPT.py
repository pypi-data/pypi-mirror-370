# -*- coding: utf-8 -*-

__version__   = '1.1.1'
__author__    = "Avinash Kak (kak@purdue.edu)"
__date__      = '2025-August-19'   
__url__       = 'https://engineering.purdue.edu/kak/distGPT/babyGPT-1.1.1.html'
__copyright__ = "(C) 2025 Avinash Kak. Python Software Foundation."


__doc__ = '''

babyGPT.py

Version: ''' + __version__ + '''
   
Author: Avinash Kak (kak@purdue.edu)

Date: ''' + __date__ + '''



@title
THE QUICKEST WAY TO START USING babyGPT:

    1.  Download the module code archive by clicking on the "gztar" link shown above.
        Unpack and install the archive by following the instruction in the
        INSTALLATION section of this documentation page.
        
    2.  Next, download the training dataset by clicking on the link "Download the
        text datasets for babyGPT" shown above.  See the Section "Training Datasets
        Provided" for further details.

    3.  Now enter the Example subdirectory of the distribution and enter the pathname
        to the training data in the script

                  create_base_model_with_buffered_context.py

        The pathname is the value of the variable 'articles_dir' near the beginning of
        the script.

    4.  Finally, execute the script named above.  That's all!



@title
CHANGE LOG:

Version 1.1.1:

    I have made further enhancements to the tokenizer training code in this version
    in order to discard the superfluous tokens, these being tokens that contribute
    almost nil to the downstream learning tasks.  For example, if the tokenizer
    training has learned two tokens 'abc' and 'abcd' and both predict exactly the
    same set of corpus words, you can discard one of the two tokens without affecting
    the overall expressive power of all the tokens learned. Additionally, since
    unsupervised learning requires estimating the maximum-likelihood probabilities
    for the next token over all the possibilities at that position, I believe that
    getting rid of the superfluous tokens can only reduce the noise in the estimation
    process. I refer to getting rid of the superfluous tokens as "cleaning up of the
    tokenizer vocabulary" which this module implements in the form of a function
    called "post_training_cleanup()" for the inner class TrainTokenizer.  As shown by
    the example script create_base_model_with_buffered_context.py in the Examples
    directory, I call the function "post_training_cleanup()" after I have trained a
    tokenizer with the function "train_tokenizer()".

Version 1.1.0:

    There was a module packaging error with 1.0.9.  I have fixed the problem in
    1.1.0.

Version 1.0.9:

    This version applies filtering to the training corpus for improving both the
    tokenizer and the working of the transformer network for next token prediction.
    Text files downloaded from the internet --- and especially the news media
    articles --- include long URL strings that should play no role in the training of
    a tokenizer or the learning required by the transformer network. (It is not
    uncommon for the URL strings to consist of hundreds of characters.)  Version
    1.0.9 accepts a string for downstream processing only if it is shorter than 20
    characters. I chose 20 because (according to Google) the average word length in
    English is only 5 and "virtually all, very close to 100%, of English words have
    fewer than 20 letters." Words that are longer than 20 characters tend to be
    mostly scientific or technical jargon.

Version 1.0.8:

    This is a PyTorch-Lightning compatible version of babyGPT. It is not so uncommon
    today for a university lab to deploy multiple low-cost GPUs for training a
    network. Using more than one GPU requires refactoring your code so that it
    conforms to the Lightning API.  Version 1.0.8 is an attempt in that direction. In
    addition to code reorganization, I have also made other minor changes to make the
    code more efficient.  For example, I eliminated a not-really-needed inner-loop in
    the overall training loop for the transformer network.  [IMPORTANT: You can still
    use this version for single-GPU based training.  The code will automatically
    detect the number of GPUs available and proceed accordingly.]  Finally, note that
    I have tested Lightning based execution of the code with only the DDP
    (Distributed Data Parallel) strategy for multi-GPU processing.  With this
    strategy, the computational graph created for the model has to fit in each GPU.
    So you cannot construct a larger model just because you are using Lightning for
    multi-GPU support.  All that you get (with the DDP strategy) is that the learning
    process will digest more data faster.  For example, if you are using a 2-GPU VM,
    your effective batch size will double because the two GPUs will be consuming the
    batches in parallel.

Version 1.0.7:

    There was an error in the definition of BasicDecoderWithMasking that I have fixed
    in this version.  Despite the error, the module worked as intended but not as
    efficiently as one would have expected.

Version 1.0.6:

    I have fixed the error that caused the predicted tokens to be shifted by one
    position vis-a-vis the ground-truth tokens.

Version 1.0.5:
    
    Had a URL error in the setup.py of the previous version. The rest of the module
    remains unchanged.

Version 1.0.4:

    This is the first public release version of the module. This module was created
    for the Deep Learning class at Purdue University.


@title
INTRODUCTION:

    SPECIFIC GOALS FOR THIS MODULE:

    1) To introduce the students in Purdue's Deep Learning class to the foundational
       concepts in how to create a Base Language Model through self-supervised
       learning.  Large Language Models start out as Base Models that are
       subsequently fine-tuned with reinforcement learning.  The focus of this module
       is solely on Base Modeling.

    2) To demonstrate small-scale large-language modeling (SS-LLM) that, for
       educational purposes, can be run in the hardware available in a typical
       university lab.

    3) To create a self-contained module that, given a set of media URLs, will
       download the articles from those websites (assuming they are not behind
       paywalls), train a BPE tokenizer for the corpus of the articles collected,
       create a Base Model from the corpus, and, subsequently, let you play with the
       model using the prompting script in the module.

    My main goal in babyGPT is to demonstrate that, for the purpose of teaching and
    learning, it is possible to create a small-scale end-to-end implementation that
    downloads a corpus of news articles, trains a BPE tokenizer if you need a new one
    for the domain of the corpus you have collected, and, finally, uses the corpus
    for training an autoregressive model for next-token-prediction based on
    unsupervised learning. After you have trained the model, you can test it with the
    prompting script that is included in the Examples directory.


    LANGUAGE MODELING AND UNSUPERVISED LEARNING:

    There is no denying the fact that the recent advances in chatbots have set the
    world on fire. It's truly amazing to see a chatbot returning (most of the time) a
    smooth-reading well-structured narrative in response to a prompt. As if that were
    not enough, it can also supply you with variants of the same narrative depending
    on how you prompt it and your randomization settings for the bot.

    One would think that this degree of competency shown by a chatbot would require a
    vast amount of human annotated data for training the neural networks used for the
    bot.

    The truth is exactly the opposite.  Most of the learning that takes place in
    order to train a chatbot is unsupervised --- that is, without any human
    supervision. The bot is given the simplest of the goals: To predict the next
    token given the tokens that have been seen so far.  To master this goal, the bot
    needs zero supervision.  All it needs to do is to use its neural network to make
    a prediction for the next token.  And, at training time, should this prediction
    be wrong, to estimate the error made, and then to backpropagate that error while
    adjusting the learnable weights in the network.  Until not too long ago most
    people would have thought that this type of learning would be much too weak to be
    of any practical use. But, as in all engineering, you cannot argue with something
    that actually works.  One great thing that has come out of AI research of the
    last two decades is that unsupervised learning not only works, it actually lends
    itself to designing powerful data driven frameworks without too much human
    intervention.


    TRANSFORMERS:

    The unsupervised learning of the sort described above is best implemented with
    Transformers. (See my material for the Week 13 lecture at Purdue's Deep Learning
    class for a detailed presentation on how one can implement an English-to-Spanish
    translation framework using Transformers.)  And central to a Transformer-based
    architecture is the notion of Attention.  Attention means the extent to which
    each element at the input to a neural network attends to every other element in
    the same input.  For example, in a network for language translation, the network
    would use Attention to figure out the significance of each token in a
    source-language sentence to every other token in the same sentence.  If "car" was
    one of the tokens in a sentence at the input and a subsequent clause in the same
    sentence used the pronoun "it" that pointed to that car, the network would be
    able to figure out the connection between the "it" and the "car" tokens through
    Attention.  Along the same lines, the network would use Cross Attention to figure
    out the importance of each token in the source language to the different tokens
    in the target language.  As you can imagine, understanding such connections
    between the tokens would be critical to any network that is learning how to
    translate a source language sentence into a target language sentence.


@title
THE MAJOR COMPONENTS of babyGPT:

    babyGPT module contains the following Python classes:

             (1) ArticleGatherer 

             (2) ArticleDataset              [supplies the data downloader for training]

             (3) TrainTokenizer 

             (4) TransformerFG               [borrowed from Transformers in DLStudio]

             (5) MasterDecoderWithMasking;   [borrowed from Transformers in DLStudio]

             (6) PromptResponder

    In what follows, I'll introduce each of these components one by one.  Each
    component is a separate inner class of the main module class babyGPT.


    @tag1
    ArticleGatherer:

    About the ArticleGatherer, you supply it with a list of URLs to media news sites.
    It then uses the Newspaper module (which understands the structure of a typical
    news HTML file) to download the articles from each of those URLs.  It is
    important to keep in mind that ArticleGatherer skips over non-HTML article files
    at the media websites. Unfortunately, many popular news websites now hide their
    content behind paywalls implemented with JavaScript.  [Examples of such websites
    include www.nyt.com, www.wsj.com, www.bbc.com, etc.] For obvious reasons, if the
    list of the URLs you provide ArticleGatherer consists of mostly such websites,
    the size of the corpus you create for experimenting with babyGPT could be much
    too small to be of any use.


    @tag1
    ArticleDataset:

    After you have used ArticleGatherer to download the news articles for the
    training corpus, the next thing you are going to need is a dataloader. That's
    exactly what's provided by the ArticleDataset class.  It randomly shuffles all
    the articles gathered and creates a number of dataloading streams equal to the
    batch-size that you are using for training babyGPT. The data input for the i^th
    batch instance is provided by the i^th stream. Logically speaking, you can think
    of each stream as a concatenation of the news articles that were randomly chosen
    for that batch instance.


    @tag1
    TrainTokenizer:
    
    Tokenizers play a critical role in language modeling because they create a
    bounded vocabulary of the tokens that the language model must understand. This is
    done by using a split-and-merge approach in which you start by considering each
    different word in your corpus as a sequence of the most basic symbols, which can
    be ASCII characters as in the WordPiece tokenizer, or the individual bytes, as in
    the BPE (Byte Pair Encoding) tokenizer.  Subsequently, you form subwords by,
    first, merging the most basic constituents like the bytes and, then, merging
    smaller subwords into longer subwords, on the basis of the frequencies of the
    merged subwords vis-a-vis the frequencies of the components that were merged. The
    merging process continues until you have reached the specified vocabulary size.
    What this logic implies is that if a long word in the corpus occurs sufficiently
    frequently, it will be represented by a single token.  On the other hand, a
    relatively short word that occurs rarely in the original corpus could be
    decomposed into shorter tokens.  It is in this manner that, with the WordPiece
    tokenizer, the BERT LLM has a vocabulary of around 30,000 tokens and, with the
    BPE tokenizer, the GPT-3 has a vocabulary of 50,000 tokens. Without such
    tokenization, the size of the vocabulary could grow continuously with the the
    size of the corpus.  As you can imagine, if a language modeler is ingesting
    terabytes of text, the vocabulary of the words it sees could run into millions.
    It is not possible to devise the probability-based logic for next-word prediction
    if your underlying vocabulary is unbounded.

    The module comes with a pretrained tokenizer with a vocab size of around 50,000
    tokens.  I trained this tokenizer using the babyGPT module on the "Athlete News"
    dataset created by Adrien Dubois. The name of the tokenizer JSON in the Examples
    directory is like: "XYZ_babygpt_tokenizer_PQRST.json".  The prefix "XYZ" says
    that JSON was created with the tokenization code in version X.Y.Z of babyGPT.
    And "PQRST" is an integer that is the actual size of the token vocab.

    Starting with Version 1.1.1, you will find the tokenizer named above in a
    subdirectory named "tokenizer_outputs" in the Examples directory of the distro.
    You will also find a cleaned version of the tokenizer in a subdirectory named
    "cleaned_tokenizer_outputs".


    @tag1
    TransformerFG:

    About the TransformerFG component of babyGPT, as mentioned already, language
    modeling is best carried out with Transformer based implementations. To that end,
    I borrowed TransformerFG from DLStudio's Transformers module.  TransformerFG is
    my implementation of the concept of the Transformer as proposed by Vaswani et
    al. in their seminal paper "Attention is All You Need."  The suffix "FG" stands
    for "First Generation."


    @tag1
    MasterDecoderWithMasking:

    The MasterDecoderWithMasking part of babyGPT has also been borrowed from
    DLStudio's Transformers module.  To see the need for this component, note that
    unsupervised learning that is needed for autoregressive language modeling only
    uses the Decoder side of the Encode-Decoder architecture that would otherwise be
    needed for a Transformer-based framework for translating one language into
    another. An example of such a framework is presented in the notes for my Week 14
    lecture at Purdue's Deep Learning class. That framework has two decoder
    implementations: MasterDecoder and MasterDecoderWithMasking.  If you are engaged
    in autoregressive modeling, you have no choice but to use the "WithMasking"
    version of the decoder.  As to the reason for the "Master" prefix in the name of
    the decoder, language modeling typically requires a number of Transformer layers,
    with each layer using multiple Attention Heads to calculate what's known as Self
    Attention. In my DLStudio code, I refer to this layered organization of the
    Transformers as MasterEncoder and MasterDecoder, and to each Transformer layer as
    the BasicEncoder and the BasicDecoder.  

    Note that there's an interesting difference between the decoder logic as used in
    language translation and what you need for unsupervised learning in a GPT: When
    used for language translation, the decoder would also calculate Cross Attention,
    which is the attention between each element of the data coursing through the
    decoder and all the elements at the final output of the encoder.  The decoder as
    used for unsupervised learning in a GPT only needs to calculate Self Attention.


    @tag1
    PromptResponder:

    About the final component of babyGPT, PromptResponder, its purpose is to put the
    trained babyGPT model to use by having it respond appropriately to the prompts
    supplied by a user.  Given a prompt in the form of a sentence fragment, the
    PromptResponder uses its next-token prediction ability to keep on generating the
    tokens until it reaches the end-of-sentence token or until it has generated a
    specified number of sentences through this process.



@title
DEALING WITH THE PROBLEM OF CONTEXT DISRUPTION CAUSED BY THE "<SOS>" TOKEN:

    What comes in the way of training babyGPT well are the textual discontinuities
    created by how a batch is constructed for each new iteration of training.  As
    explained elsewhere in this doc page, the list of all the documents in the
    training corpus is first randomized and then divided into a number of token
    streams, with one stream for each batch instance. (This randomization of the
    files and the division into token streams is carried out afresh at the beginning
    of each epoch.)  Subsequently, when a fresh batch is needed, for each batch
    instance you "draw" from its corresponding stream a "Context Window" number of
    tokens. The special <SOS> token is placed at the beginning of each such token
    sequence.

    This insertion of the <SOS> token disrupts the continuity of the token streams,
    as you can well imagine, and it violates the main point of the learning involved
    which is to learn the continuity properties of the text. Since these continuities
    are context dependent, it would be fair to say that the <SOS> token causes a
    context disruption for the token that comes after <SOS> at the beginning of each
    batch instance.  Over the years, various strategies have been proposed to
    circumvent this problem, one of the most recent being the "sliding-window based
    Attention" as presented by Beltagy, Peters, and Cohan in their 2023 paper
    "Longformer: The Long-Document Transformer".  In this approach, a fixed-sized
    window is used to calculate the attention at the token that is at the center of
    the window.  In this manner, what is calculated for Self Attention is the extent
    to which each token attends to the W/2 tokens on each side of the token at the
    center.  As the authors say: "Using multiple stacked layers of such windowed
    attention results in a large receptive field, where top layers have access to all
    input locations and have the capacity to build representations that incorporate
    information across the entire input."

    In keeping with the spirit of babyGPT, I have used a much simpler approach to
    deal with the context disruption problem caused by the <SOS> token.  My solution
    is based on an idea I call "Context Buffer".  The Context Buffer for each token
    sequence in CURRENT batch consists of the last n tokens in the corresponding
    token sequence in the PREVIOUS batch.  These last n tokens, inserted after the
    <SOS> token in the current batch, provided the context for the prediction at the
    first token positions in the current batch.

    To elaborate, let's assume that N is the size of the Context Window for your
    Transformer based processing of text and n is the size of the Context Buffer.  At
    every training iteration, for each batch instance you will pull N fresh tokens
    from the dataloader.  You will prepend the n last tokens for the same instance in
    the previous batch to the sequence of N tokens supplied by the dataloader for the
    current batch.  This will result in n+N tokens for transformer-based
    processing. I refer to n+N as the max_seq_length for which you have designed the
    transformer.

    It is interesting to note that the above mentioned problem with context
    disruption does NOT arise with sentence-based language modeling (as in BERT)
    since <SOS> is what you would want to use for designating the start of a
    sentence.  (For such learning, you would also use another token, denoted <EOS>
    for the "End of Sequence" indication.)



@title
CONFORMING TO THE LIGHTNING API:

Right off the bat, your code must create an instance of the Lightning's Trainer
class.  In my code, this call looks like:

        trainer =  Lightning.Trainer(devices=-1, 
                                     accelerator="gpu", 
                                     strategy='ddp', 
                                     enable_progress_bar=False,
                                     logger=logger,
                                     max_epochs=-1,
                                     log_every_n_steps=100
                                    )

About the constructor parameters used above, I have used "devices=-1" because I want
babyGPT to run without any changes in both my laptop for debugging and code
development purposes and my 2-GPU VM in our lab cloud.  With the option "devices=-1",
Lightning will discover the number of GPUs available and automatically set "devices"
to that number.  Understanding the option "strategy='ddp'is important if you want to
have realistic expectations of what Lightning can do for you.  The "ddp" strategy
stands for "Distributed Data Parallel".  This strategy launches a number of processes
that are executed in parallel, with one process for each GPU.  While each process
creates its own instance of the dataloader and has its own training loop for forward
propagation of the data and backpropagation of the loss gradients, the processes are
synchronized for updating the model parameters.  The updating of the learnable
parameters is synchronized in the sense that it is based on the backpropagated loss
gradients in all of the processes.

Subsequently, you must call "fit()" on the Trainer instance with at least the two
required arguments: the model you want Lightning to train and the dataloader to be
used for training.  Here's an example of this call in babyGPT:

        trainer.fit( model=master_decoder,  
                     train_dataloaders= StreamingDataModule(
                                            data_source=dataloader,
                                            context_window_size=dataloader.context_window_size,
                                            batchsize=dataloader.batch_size,
                                            context_buffer_size=dataloader.context_buffer_size,
                                            inv_lookup_fn=dataloader.inverse_lookup)
                                        )

The "model" that is in the first argument to "trainer.fit()" is a network that you
want Lightning to train; this model must be subclassed from the class
'Lightning.LightningModule'. Starting with version 1.0.8, in babyGPT, it is the class
MasterDecoderWithMasking that is derived from 'Lightning.LightningModule'.

If you have been following the evolution of babyGPT, you will see a sea change
between the versions 1.0.7 and 1.0.8 for how the class MasterDecoderWithMasking is
implemented. You see, a network that is meant to be learned with Lightning must have
following methods defined for it: training_step(), train_dataloader(), and
configure_optimizers().  The first, training_step(), has the code that is meant to be
executed at every iteration of training.  The second, train_dataloader(), must return
a dataloader that is implemented as a Python generator.  That is, the dataloader must
return a new batch through a 'yield' statement in a 'while' loop.  Lightning can
invoke the train_dataloader() automatically to fetch the next batch for a new
training cycle.  Finally, about the function configure_optimizers(), note that
Lightning allows for only specific types of optimizers and learning-rate schedulers
for the optimizers.

In the code that follows, the required three functions named above are in the
definition of the class MasterDecoderWithMasking. Note that it is the network created
for this class that carries out autoregressive modeling of a text corpus.  [In the
previous version of the module, v.1.0.7, all of this code was in the method
"run_code_with_buffered_context_for_training_TransformerFG" of the top-level babyGPT
class.] 

In addition to the above, here are some pointers relevant to making a software module
ready for Lightning: (1) For single GPU based processing, when you cast a tensor to
type CUDA, it is obvious to the system that you want to prepare that tensor for its
storage in the memory of the GPU that is available.  However, when you have multiple
GPUs, how do you cast a tensor to be of type CUDA for a specific GPU?  Here is an
example of how to best address this problem:

       mask = torch.ones(1, device=input_sequence.device, dtype=torch.long)   

The goal here is to create a mask that is needed for autoregressive learning. Recall
from my Week 14 lecture, autoregressive modeling is all about predicting the next
token based on the tokens seen so far in the input. This requires progressively
masking the input sequence to indicate to the model how much of the input sequence to
use for the next token prediction. That is, for a fresh iteration of the training
cycle, you will start with the mask consisting of a single 1, which tells the model
to make a prediction for the token at second position in the input based on its
knowing just the first token. Subsequently, you will concatenate another 1 to the
mask and now the model will try to make a prediction for the third token in the input
based on the its knowledge of the first two tokens.  In the code line shown above,
what you see the mask being initialized with a single '1' for a new input sequence.

The important point is that the initialization of the mask tensor shown above must
take place separately for each of the GPUs available to Lightning. As it turns out,
Lightning creates a separate process for each of the GPUs. The question then becomes:
How to inform each process as the CUDA type of the tensor being created as shown
above. As can see, it is done with the simple expedient of declaring the "device" to
be the same as for the "input_sequence".  That makes completely unambiguous the
destination of the new mask tensor. Regarding the "input_sequence" tensor, for the
DDP (Distributed Data Parallel) strategy, each GPU process runs the dataloader
separately.  Therefore, each process will create its own version of the
"input_sequence" tensor.

Another thing to bear in mind about Lightning is that it assumes that all of the
tensors created in the implementation for "training_step()" are meant to be of type
CUDA. So you are spared the need to append ".cuda()" or ".to(device)" to the tensor
initializations as is common for the case of single-GPU based code.



@title
GETTING RID OF THE SUPERFLUOUS TOKENS

Version 1.1.1 includes a new function named "post_training_cleanup()" defined for the
TrainTokenizer class that you can invoke after you have trained a tokenizer in order
to get rid of superfluous tokens.  A token A is superfluous vis-a-vis another token B
if A is a substring of B and if the number of the corpus words that contain the
tokens A and B are exactly the same.  

When you invoke the function "post_training_cleanup()", the cleaned-up tokenizer JSON
is deposited in the subdirectory:

            cleaned_tokenizer_outputs

Ordinarily, the tokenizer JSON that is produced by the function "train_tokenizer()" 
is deposited in the subdirectory:

            tokenizer_outputs



@title
EXTENDING A PREVIOUSLY LEARNED TOKENIZER JSON:

Let's say you have trained a tokenizer with a target vocabulary of 40,000 and you
want to extend the target vocabulary to, say, 50,000 without having to retrain the
whole thing from scratch.  How does one do that?  It is an important question in a
university lab because tokenizer training is CPU intensive and can take days depending
on your hardware and the size of the target vocabulary.

Version 1.1.1 allows you to extend the target vocabulary size for a previously
trained tokenizer.  It is accomplished with the function 

              extend_tokenizer_with_additional_training()

defined for the inner class TrainTokenizer. The starting point for using this function
should be the following script in the Examples directory:

              extend_previously_trained_tokenizer.py

Note that this script expects to command-line arguments, with the first being the 
pathname to the previously trained JSON and the second the new target vocab size.
Here's an example:

   python3   extend_previously_trained_tokenizer.py   tokenizer_outputs/111_babygpt_tokenizer_20025.json    30000

You'll obviously need to make sure that the numbers "111", "20025", and "30000"  
are specific to your request.



@title
EXAMPLES OF THE OUTPUT PRODUCED DURING TRAINING:

The examples I have shown below are based on the following assumptions:

--  You are using the "Athlete News" dataset that you can download from the module
    website at Purdue.  As mentioned, this dataset was derived by Adrien Dubois from
    the 2017-2018 news reports.

--  You are training the model with the following config parameters:


                    GPUs used   :   TWO NVIDIA A5000 (each with 24 GB)
          Max Sequence Length   :   55
                   Batch Size   :   50
               Embedding Size   :   384                                        
           Transformer Stages   :   6 
    Number of Attention Heads   :   8 
                Learning Rate   :   10^-4  (with Cosine scheduler)
                 Warmup Steps   :   4000


--  You are running the following script in the Examples directory of the
    distribution:

            create_base_model_with_buffered_context.py                       

    
The script named above will show the following sort of output every 100 iterations.
For each output, it will randomly select four out of for 50 batch instances and present
the information arranged as follows:


            Ground-truth

            GT Token Seq

               Predicted

             Detokenized


where "Ground-truth" is a segment of the text extracted from the downloader for each
batch instance; "GT Token Seq" is tokenized version of the ground-truth; "Predicted"
is the sequence of predictions at each token position by the transformer; and
"Detokenized" is the output of the decoder that joins the tokens back into words.  To
help out with detokenization, babyGPT inserts underscores between the whole words
that are dropped in the detokenization step.  You can see these underscores in the
outputs shown for "GT Token Seq".

In the rest of this section, I have displayed an example of the output produced for
each epoch:


@tag1
Epoch 0 example:

Ground-truth:  ” It was just the Lakers ’ third loss in 11 games since the All - Star break ,  but their fourth against the Warriors_
GT Token Seq: . ” It _ was _ just _ the _ Lakers ’ third _ loss _ in _ 11 _ games _ since _ the _ All - Star _ break , but _ the ir _ fourth _ again st _ the _ War ri or s _
   Predicted: _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
 Detokenized: _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _


@tag1
Epoch 1 example:

Ground-truth: _with a seven - point lead .  However ,  the Warriors caught up soon enough and then left them in a trail of smoke
GT Token Seq: _ with _ a _ seven - point _ lead . How ever , the _ War ri or s _ caught _ up _ soon _ enough _ an d _ then _ left _ them _ in _ a _ tra il _ of _ smo ke
   Predicted: _ of _ a _ two - time _ lead _ The ever, the _ War ri or s _ are _ up _ a _ to _ to d _ the _ the _ the _ to _ the _ row _ _ of _ the y
 Detokenized: _of a two - time lead Theever,  the Warriors are up a to tod the the the to the row _of they


@tag1
Epoch 2 example:

Ground-truth: Feb .  2 ,  2018 ,  in Sacramento ,  Calif .  ( AP Photo / Rich Pedroncelli ) Golden State Warriors guard Stephen Curry goes to the
GT Token Seq: Fe b . 2 , 2018 , in _ Sacramento , Cali f . ( AP _ Photo / Rich _ Pe d ron cel li ) Golden _ State _ War ri or s _ guar d _ Stephen _ Curry _ go es _ to _ the
   Predicted: Fe b. 22, 2018. in _ the, Cali f. ( AP _ Photo / Mark _ J der le _ _ ). _ State _ War ri or s _ forward d _ Stephen _ Curry _ ( _ _ to _ the
 Detokenized: Feb.  22,  2018.  in the,  Calif.  ( AP Photo / Mark Jderle _ ). State Warriors forwardd Stephen Curry ( _to the


@tag1
Epoch 3 example:

Ground-truth: got a Finals MVP [ Andre Iguodala ] that comes off their bench .  ” James pointed out that the Warriors are
GT Token Seq: got _ a _ Finals _ MVP _ [ An d re _ Igu od al a ] that _ co mes _ off _ the ir _ bench . ” James _ poin te d _ out _ that _ the _ War ri or s _ are
   Predicted: got _ to _ lot _ MVP _ an Stephen d re _ Igu od al a _, _ is mes _ to _ the _ _ season _ The The _ is te d _ to _ the _ the _ War ri or s _ have
 Detokenized: got to lot MVP anStephendre Iguodala_, ismes to the _season TheThe isted to the the Warriors have


@tag1
Epoch 4 example:

Ground-truth: _Warriors ( 58 - 24 ) vs .  No .  7 San Antonio Spurs ( 47 - 35 ) How to watch Game 5 Date : Tuesday ,  April 24_
GT Token Seq: _ War ri or s _ ( 58 - 24 ) vs . No . 7 _ San _ Antonio _ Spurs _ ( 4 7 - 35 ) How _ to _ watch _ Ga me _ 5 _ Da te : Tuesday , April _ 24 _
   Predicted: _ War ri or s _ in 1 - 0 ).. Cleveland _ 1 _ seed _ Antonio _ Spurs : ( 10 ) ) 3 ) an _ did _ watch _ the me _ 1 _ of vi _ " _ June _ 22,
 Detokenized: _Warriors in1 - 0 ).  Cleveland 1 seed Antonio Spurs : ( 10 ) ) 3 ) an did watch theme 1 ofvi " June 22,


@tag1
Epoch 5 example:

Ground-truth: Kevin Durant and Klay Thompson ,  the Warriors lost Draymond Green in the second quarter to a bruise in_
GT Token Seq: K ev in _ Durant _ an d _ K lay _ Thom p son , the _ War ri or s _ lo st _ Dra y mon d _ Green _ in _ the _ second _ quarter _ to _ a _ bruise _ in _
   Predicted: K lay in _ Durant _ an d _ Dra lay _ Thom p son _ Dra _ War ri or s _ an st _ to y mon d _ Green _ an _ the _ second _ half _ to _ a _ four _ in _
 Detokenized: Klayin Durant and Dralay Thompson Dra Warriors anst toymond Green an the second half to a four in_


@tag1
...and so on



For truth in advertising, I must hasten to add that, in what you see above, I have
chosen some of the better looking examples for each epoch.  For every good output
example like those shown above, you will see a large number meaningless gibberish
examples.  As you would expect, at the beginning of training, all output is mostly
gibberish.  However, as the training continues, you begin to see more and more
examples of the output that makes sense.



@title
INSTALLATION:

    The babyGPT class was packaged using setuptools.  For installation, execute
    the following command in the source directory (this is the directory that
    contains the setup.py file after you have downloaded and uncompressed the
    gzipped tar archive for the module):
 
            sudo python3 setup.py install

    On Linux distributions, this will install the module file at a location that
    looks like

             /usr/local/lib/python3.10/dist-packages/

    If you do not have root access, you have the option of working directly off
    the directory in which you downloaded the software by simply placing the
    following statements at the top of your scripts that use the
    babyGPT class:

            import sys
            sys.path.append( "pathname_to_babyGPT_directory" )

    To uninstall the module, simply delete the source directory, locate where the
    babyGPT module was installed with "locate
    babyGPT" and delete those files.  As mentioned above, the full
    pathname to the installed version is likely to look like
    /usr/local/lib/python2.7/dist-packages/babyGPT*

    If you want to carry out a non-standard install of the babyGPT
    module, look up the on-line information on Disutils by pointing your browser
    to

              http://docs.python.org/dist/dist.html

@title
USAGE:

    If you want to use babyGPT for unsupervised learning of a base model for a text
    corpus, you would need to construct an instance of the main babyGPT class and its
    supporting classes as follows:

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
                        masking = masking
                     )
    
    dataloader = baby_gpt.ArticleDatasetWithBufferedContext(
                        gpt = baby_gpt,
                        tokenizer_json = tokenizer_json,
                        context_window_size = context_window_size,
                        context_buffer_size = context_buffer_size,
                        articles_dir = articles_dir,
                 )

    

@title 
THE Examples DIRECTORY:

    This directory contains the following four scripts for working with babyGPT:

        1.  run_gatherer.py

            This script is for collecting a corpus for experimenting with babyGPT.
            The script requires a list of URLs as article sources as illustrated
            by the following example:

                urls = ['https://finance.yahoo.com','http://cnn.com',
                        'https://sports.yahoo.com',
                        'https://purdueexponent.org','https://slate.com',
                        'https://timesofindia.indiatimes.com',
                        'http://cnn.com',
                        'https://slate.com'
                       ]

        2.  train_tokenizer.py

            If the text corpus you have collected is for a specialized domain (such
            as movies, sports, healthcare, etc.), you are likely to get better
            results from babyGPT if you first train a new tokenizer for that domain.
            You train a new tokenizer merely by invoking this script after you have
            set its variable "articles_dir" so that it points to the corpus 
            directory.


        3.  create_base_model_with_buffered_context.py

            This is the script to run if you want to create a Base Model for your
            corpus.  By Base Model I mean a language model acquired through
            unsupervised learning from a training corpus.  Since this script calls on
            the core language modeling functionality of babyGPT, you have to set a
            relatively large number of parameters in the script.  These parameters
            are shown below:

                articles_dir
                tokenizer_json 
                max_seq_length 
                context_window_size
                context_buffer_size
                batch_size 
                embedding_size
                num_atten_heads 
                num_basic_decoders 
                optimizer_params
                num_warmup_steps


        4.  interact_with_prompts.py
 
            This is the script for interacting with a trained babyGPT model through
            prompts.  The idea is that you supply a small number of words (as, say,
            the beginning of a new thought) as a prompt and the model supplies the
            rest of the words to complete the thought.  At this time, the model
            extends your prompt until it reaches a period (or the end dictated by the
            size of the "max_seq_length" parameter.


@title
THE TRAINING DATASETS PROVIDED:

    Click on the following link near the beginning of this documentation page:

                    "Download the text datasets for babyGPT" 

    in order to download the following training data archive

                          datasets_for_babyGPT.tar.gz

    Save the archive in the Examples directory of the distribution.  Now execute the
    following command:

                 tar zxvf datasets_for_babyGPT.tar.gz

    This command will create a 'data' subdirectory in the 'Examples' directory                                                  
    and deposit the datasets mentioned below in that subdirectory:

                 saved_Adrien_News_Articles_56M

                 saved_articles_dir_12M

    The first is the "Athlete News" corpus created by Adrien Dubois. The suffix "56M"
    in the name of the corpus refers to the fact that the corpus consists of roughly
    56 Million multi-byte Unicode characters with utf-8 encoding.

    The second is a much smaller corpus for debugging purposes.  It is based on the
    news articles I downloaded with the "run_gatherer.py" script in the Examples 
    directory.



@title
BUGS:

    Please notify the author if you encounter any bugs.  When sending email,
    please place the string 'babyGPT' in the subject line to get past his
    spam filter.


@title 
ACKNOWLEDGMENTS:

    I must thank Aditya Chauhan for pulling me into the world of multi-GPU training
    with PyTorch Lightning.  If you find useful any of the pointers I have provided
    for making your code compatible with the Lightning API, the primary credit for
    that should go to Aditya.  Aditya, currently pursuing a PhD in Purdue RVL, is
    also our foremost expert in OpenStack based cloud computing.  I'd also like to
    thank Amith Kashyap and Adrien Dubois, both also PhD candidates in RVL, for many
    insightful conversations about deep learning, in general, and about mult-GPU 
    computing in particular.  As previously mentioned in this page, Adrien is also 
    the creator of the "Athlete News" dataset that I provide through this module 
    webpage at Purdue.


@title
ABOUT THE AUTHOR:

    The author, Avinash Kak, is a professor of Electrical and Computer Engineering at
    Purdue University.  For all issues related to this module, contact the author at
    "kak@purdue.edu". If you send email, please place the string "babyGPT" in your
    subject line to get past his spam filter.


@title
COPYRIGHT:

    Python Software Foundation License

    Copyright 2025 Avinash Kak

@endofdocs
'''

import sys,os,os.path,copy
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as tvt
import numpy as np
import math
import random
import string
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import glob                                                                                                           
import json
import logging                 
import re
import itertools
import newspaper
from torch.utils.data import Dataset,IterableDataset,DataLoader
from collections import Counter
from newspaper import Article
import blingfire as bling                     ## has the best sentence detector
from transformers import PreTrainedTokenizerFast
from tokenizers import Tokenizer                                                                                               
from tokenizers.pre_tokenizers import Whitespace 
import lightning as L
from torch.optim.lr_scheduler import LinearLR,CosineAnnealingLR,CosineAnnealingWarmRestarts,SequentialLR
from pytorch_lightning.loggers import TensorBoardLogger


#############################################################################################################################
################################################  Top level utility functions  ##############################################

import signal

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def ctrl_c_handler( signum, frame ):             
    print("Killed by Ctrl C")                       
    os.kill( os.getpid(), signal.SIGKILL )       
signal.signal( signal.SIGINT, ctrl_c_handler )   

def gen(container):
    j = 0
    while j < len(container):
        yield container[j]
        j += 1


###%%%
#############################################################################################################################
#############################################   babyGPT Class Definition   ##################################################

class babyGPT(object):

    def __init__(self, *args, **kwargs ):
        if args:
            raise ValueError(  
                   '''babyGPT constructor can only be called with keyword arguments for 
                      the following keywords: urls, max_seq_length, batch_size, embedding_size, num_atten_heads, beta1, beta2, epsilon,
                      num_warmup_steps, masking, use_gpu, verify_text_corpus, path_saved_model''')
        max_seq_length=batch_size=embedding_size=num_atten_heads=beta1=beta2=epsilon=num_warmup_steps=masking=use_gpu=verify_text_corpus=None
        urls=path_saved_model=None

        if 'urls' in kwargs                          :   urls = kwargs.pop('urls')
        if 'max_seq_length' in kwargs                :   max_seq_length = kwargs.pop('max_seq_length')
        if 'batch_size' in kwargs                    :   batch_size = kwargs.pop('batch_size')
        if 'embedding_size' in kwargs                :   embedding_size = kwargs.pop('embedding_size')
        if 'num_atten_heads' in kwargs               :   num_atten_heads = kwargs.pop('num_atten_heads')
        if 'beta1' in kwargs                         :   beta1 = kwargs.pop('beta1')
        if 'beta2' in kwargs                         :   beta2 = kwargs.pop('beta2')
        if 'epsilon' in kwargs                       :   epsilon = kwargs.pop('epsilon')
        if 'num_warmup_steps' in kwargs              :   num_warmup_steps = kwargs.pop('num_warmup_steps')
        if 'masking' in kwargs                       :   masking = kwargs.pop('masking')
        if 'use_gpu' in kwargs                       :   use_gpu = kwargs.pop('use_gpu')
        if 'verify_text_corpus' in kwargs            :   verify_text_corpus = kwargs.pop('verify_text_corpus')
        if 'path_saved_model' in kwargs              :   path_saved_model = kwargs.pop('path_saved_model')

        if urls:
            self.urls = urls
        else:
            self.urls = None 
        if max_seq_length:                         
            self.max_seq_length = max_seq_length    
        if batch_size:
            self.batch_size = batch_size
        if embedding_size:
            self.embedding_size = embedding_size
        if num_atten_heads:
            self.num_atten_heads = num_atten_heads
        if beta1:
            self.beta1 = beta1
        if beta2:
            self.beta2 = beta2
        if epsilon:
            self.epsilon = epsilon
        if num_warmup_steps:
            self.num_warmup_steps = num_warmup_steps
        if masking:
            self.masking = masking     
        if verify_text_corpus:
            self.verify_text_corpus = verify_text_corpus
        else:
            self.verify_text_corpus = False
        if path_saved_model:
            self.path_saved_model = path_saved_model


    ###%%%
    #############################################################################################################################
    ######################################  Start Definition of Inner Class ArticleGatherer  ###################################

    class ArticleGatherer:
        """
        This script is for collecting data for experimenting with the Transformer based unsupervised learning 
        code in baby_gpt.py.  

        The articles are downloaded from the URLs that are specified by the argument 'urls' in the constructor 
        shown below.  See the script "create_base_model_with_buffered_context.py" in the Examples directory
        for how to set the URL strings for this argument.  Here are some examples:

            urls = ['https://finance.yahoo.com','http://cnn.com',
                     'https://timesofindia.indiatimes.com',
                     'https://purdueexponent.org','https://slate.com', 
                     'https://sports.yahoo.com']
    
            urls = ['http://cnn.com']
    
            urls = ['https://slate.com']
    
            urls = ['https://timesofindia.indiatimes.com']
        """
        def __init__(self, gpt, urls, articles_dir = 'saved_articles_dir'):
            ##  'urls' is a local array in which we store all the article URLs from where we want to 
            ##   download the news articles:
            self.urls = gpt.urls
            self.articles_dir = articles_dir

        def download_articles(self):
            if os.path.exists(self.articles_dir): 
                articles = glob.glob(self.articles_dir + "/*") 
                for file in articles:        
                    if os.path.isfile(file):       
                        os.remove(file)      
                    else:       
                        files = glob.glob(file + "/*")         
                        list(map(lambda x: os.remove(x), files))
            else:       
                os.mkdir(self.articles_dir)      
            master_list_article_links =  []
            for url in self.urls:
                print("\n\nDownloading from URL: %s\n\n" % url)
                scraped = newspaper.build( url, memoize_articles=False )
                for article_link in scraped.articles:
                    master_list_article_links.append( article_link.url )
                    print(article_link.url)
                print("\n\nThe number of available articles: ", scraped.size())
            print("\n\n\nHere is a dump of the article url's from all the news websites: ", master_list_article_links)
            print("\n\n\nTotal number of articles in the dump: ", len(master_list_article_links) )

            article_index = 0
            for item_url in master_list_article_links:
                if not item_url.endswith(".html"):
                     continue
                article_file_name =  self.articles_dir + "/" +  "article_" + str(article_index) + ".txt"
                FILE = open(article_file_name, 'w')
                try:
                    article = Article(item_url)
                    article.download()
                    article.parse()
                except:
                    continue
                print("downloaded ", article_file_name)
                text = article.text
                FILE.write(text)
                FILE.flush()
                FILE.close()
                article_index += 1
    


    ###%%%
    #############################################################################################################################
    ######################################  Start Definition of Inner Class TrainTokenizer  #####################################

    class TrainTokenizer:
        """
        Tokenizers play a critical role in language modeling because they create a fixed-sized vocabulary 
        for the corpus you are working with --- regardless of the size of the corpus itself.  Unless your 
        text corpus is based on a set of documents frozen in time, ordinarily, as the size of a text corpus 
        goes up, so does the size of the vocabulary --- despite the illusion to the contrary created by 
        the fixed sizes of the language dictionaries you have seen all your life.  How we express ourselves 
        is a living thing.  We are constantly inventing new words and new expressions; these form important 
        components of  what's referred to as the zeitgeist.

        Having a fixed-sized vocab is important because the loss functions used in deep-learning network 
        used for language processing are based on maximum-likelihood prediction of the next token given 
        the tokens seen previously.  That requires estimating the probabilities associated with all
        possible tokens at the next position.  As you can imagine, it would be impossible to engage in 
        such probabilistic reasoning if you did not know in advance the size of the vocabulary.

        Added in version 1.0.9: Here's an important point to remember when you are training a tokenizer 
        on media articles collected from the internet at large: The articles frequently contain long 
        URL strings that should play no role in either training the tokenizer for a new corpus or in 
        training a transformer network for next-token prediction. What makes this problem worse is that 
        such strings may consist of hundreds of characters --- because some media URLs these days 
        contain the full title of the articles they point to. In addition, parts of a URL (such as the 
        Query part) may also be encoded --- that is, consist of a seemingly gibberish sequence of
        characters.  To get rid of such strings, starting with Version 1.0.9, I filter out all strings 
        that are longer than 20 characters.  This I do both for Tokenizer training and when reading in 
        the text data for training the transformer network.
        """
        def __init__(self, corpus_directory, target_vocab_size=50000):
            import babyGPT
            version_str =  babyGPT.__version__
            self.version_str = version_str.replace(".", "")
            self.tokenizer_json_stem   =   "tokenizer_outputs/" + self.version_str + "_babygpt_tokenizer_"
            self.cleaned_tokenizer_json_stem   =   "cleaned_tokenizer_outputs/" + self.version_str + "_babygpt_tokenizer_"
            self.extended_tokenizer_json_stem   =   "extended_tokenizer_outputs/" + self.version_str + "_babygpt_tokenizer_"
            if os.path.exists(corpus_directory):
                self.corpus_dir = corpus_directory
            else:
                sys.exit("\n\n\nYour text corpus not at the specified pathname. Aborting!\n\n")
            self.unk_token = "[UNK]"                    # token for undecipherable bytes
            self.spl_tokens = ["<UNK>", "<SEP>", "<MASK>", "<CLS>"] 
            self.target_vocab_size = target_vocab_size

            ##  Since we are assuming utf-8 encoding of the text corpus, we already have
            ##  the mappings between the numbers 0 through 255 and their corresponding
            ##  tokens as would be yielded by calling the Python function chr() on the
            ##  integers between 0 and 255.  [For example, chr(255) returns the character
            ##  'ÿ'. What that means is that 255 is the Unicode code point for this symbol.]
            ##  So the first available index for a new token produced by the merge rule 
            ##  would be 256:
            self.next_index_available = 256
            ##  I use "testing_iter" for producing the intermediate results during training:
            self.testing_iter = 0                         
            self.debug = False

      
        def train_tokenizer(self):
            """
            To fully understand (and, if you wish, to modify or extend) the implementation shown for
            this function, you need to keep in mind the fact that practically all text I/O in
            modern times uses the assumption that character encoding used in a text file is
            based on Unicode and the bit patterns for the different Unicode values (also called
            Unicode code points) are as prescribed by utf-8. Unicode allows for using a 4-byte
            integer for representing all the characters in all the languages of the world
            (including languages that are yet to be discovered --- assuming there are still any
            left undiscovered). That is, under Unicode, each character in every language is
            assigned a 4-byte integer value whose bit pattern is according to utf-8 encoding
            and that makes it possible to maintain backward compatibility with ASCII and Latin1
            encoding schemes for character encoding.

            As mentioned in the doc comment associated with the class "TrainTokenizer", the
            goal of training a tokenizer is to come up with a fixed-size token vocabulary for
            an an arbitrarily sized corpus vocabulary. And, at the moment, the most commonly
            used algorithm for that purpose is BPE, which stands for "Byte Pair Encoding". The
            main idea in the iterative logic of BPE is to start out by assuming that your token
            vocab consists of the 256 different possible bytes and then considering each
            corpus word as a sequence of such tokens (initially referred to as subwords).
            Subsequently, you search for the most frequently occurring pairs of contiguous
            subwords and you merge them together into a larger subword. You continue this
            iterative logic until the token vocab has reached the target size.
            
            The logic described above makes sense when the training corpus consists of just the
            English documents (when the character encoding could be based on the 7-bit ASCII)
            or the documents in European languages (in which the character encoding could be
            the 8-bit Latin-1 extension of ASCII).  However, if the goal is to create a
            language-agnostic tokenizer, you must assume that you are dealing with the Unicode
            encoding for the characters, implying that you are dealing with multi-byte
            character representations in your text files and that the bit patterns used for the
            individual characters are according to the utf-8 standard.

            Keeping the above in mind, it would be more appropriate to refer to the algorithm I
            have implemented below as CPE for "Character Pair Encoding" as opposed to BPE.
            (Obviously, for purely English documents and documents in European languages, it
            would automatically revert to BPE because for those languages the utf-8 encodings
            are single-byte and exactly the same as ASCII and Latin-1.) CPE is based on the
            default behavior of Python's built-in functions chr() and ord(). The ord() function
            returns the Unicode code point for a given character and the chr() takes an integer
            argument, which it treats as a Unicode code point, and returns the corresponding
            character. Try entering 'chr(32000)' in interactive Python and see what you get.
            And, as you would expect, 'ord(chr(32000))' returns 32000.

            The role played by the Unicode-related behavior of chr() and ord() is mostly
            implicit in the implementation shown below.  For example, in the function
            'subword_for_num_seq( num_seq )' the goal is to map a sequence of integer indexes
            to subwords. This function uses two dictionaries 'num_to_char_dict'and
            'ints_to_subwords_dict', with the first a mapping from the integer indexes to the
            individual characters found so far as the training corpus is digested one file at a
            time, and the second a mapping from the subwords created so far to their integer
            indexes. Note that the statement where the text files are read uses the following
            invocation of 'open()': "with open( filedoc, encoding='utf8', errors='ignore' ) as
            f".

            Tokenizer training steps: 

            -- Start with a base vocabulary for the tokens that consists of all 256 integer
               values that can be taken on by a byte.  Expand on the base vocabulary as
               individual multi-byte characters are discovered in the training corpus. This
               makes the base vocabulary dynamic and specific to a training corpus.

            -- Search through consecutively occurring numeric codes for the Unicode characters
               to find the pair that is the most frequent in terms of the number of corpus
               words that contain the pair.

            -- Merge the two parts of the pair thus discovered to form a new token (referred to 
               as a subword during the training iterations).  Store each merge in a list that
               you will need later when constructing a JSON for the tokenizer.

            -- Replace the pair thus discovered in the token representations for all the words 
               with the new subword.
           
            -- Apply the logic described above iteratively until the size of the tokenizer
               vocab has reached the prescribed value.

            Note that the size of the tokenizer vocabulary is sum of the size of the Base Vocab
            and the number of merges.  As mentioned, the Base Vocab consists of the unique
            individual characters (which may be multi-byte characters) in the training corpus.
            """
            def word_as_num_seq(word):
                for char in list(word):
                    if char not in char_to_num_dict:
                        char_to_num_dict[char] = self.next_index_available
                        ints_to_subwords_dict[ self.next_index_available ] = char
                        self.next_index_available += 1       
                return [char_to_num_dict[char] for char in list(word) ]
            
            def get_str_token( num ):
                """
                Note that ints_to_subwords_dict is what becomes the vocab eventually.  We make the
                conversion by reversing the <key,num> pairs in ints_to_subwords_dict.
                """
                if num in num_to_char_dict:
                    return num_to_char_dict[num]
                elif num in ints_to_subwords_dict:
                    return ints_to_subwords_dict[num]
                else:
                    sys.exit("\n\n[get_str_token]  ints_to_subwords_dict has no merge rule for the int token %d\n\n" % num)
            
            def subword_for_num_seq( num_seq ):
                subword = ""
                for num in num_seq:
                    if num in num_to_char_dict:
                        subword += chr(num)
                    elif num in ints_to_subwords_dict:
                        subword += ints_to_subwords_dict[num]
                    else:
                        sys.exit("\n\n[subword_for_num_seq] ints_to_subwords_dict has no merge rule for the int token %d\n\n" % num)
                return subword
            
            def update_tokenizer_dict( tokenizer_dict, most_frequent_pair, new_token_as_num ):
                new_tokenizer_dict = {word : [] for word in tokenizer_dict}
                for word in tokenizer_dict:
                    str_rep = ",".join(str(i) for i in tokenizer_dict[word])
                    to_be_replaced_pair =  r"\b" +  ",".join(str(i) for i in most_frequent_pair) + r"\b"
                    replacement = str(new_token_as_num) 
                    output_str= re.sub(to_be_replaced_pair, replacement, str_rep)
                    new_tokenizer_dict[word]  =  [int(i) for i in output_str.split(",")]
                return new_tokenizer_dict
            
            
            def find_best_ngram_and_update_word_tokens_dict(tokenizer_dict):
                all_consec_pairs_dict = { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:] ) ) for word in tokenizer_dict }
                all_consec_triples_dict =   { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:],  tokenizer_dict[word][2:] ) ) 
                                                                                                                     for word in tokenizer_dict }
                all_consec_quads_dict   =   { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:],  tokenizer_dict[word][2:], 
                                                                                        tokenizer_dict[word][3:] ) ) for word in tokenizer_dict }   
                all_consec_all_ngrams_dict = {}
                for word in all_consec_pairs_dict:
                    if word in all_consec_triples_dict and  word in all_consec_quads_dict:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word] + all_consec_triples_dict[word] + all_consec_quads_dict[word]
                    elif word in all_consec_triples_dict:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word] + all_consec_triples_dict[word]
                    else:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word]
                all_consec_all_ngrams_dict  =   {word : all_consec_all_ngrams_dict[word] for word in all_consec_all_ngrams_dict 
                                                                                                      if len(all_consec_all_ngrams_dict[word]) > 0}
                most_frequent_ngram = list(Counter( list( itertools.chain(*all_consec_all_ngrams_dict.values()) ) ).keys()) [0]
                string_for_merges_array = "%s %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]))
                merges.append( string_for_merges_array )
                subword_for_most_frequent_ngram  =  subword_for_num_seq( most_frequent_ngram )

                vocab_word_to_merges_dict[self.next_index_available] = string_for_merges_array

                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter: %d] Will merge the following subwords for the new most frequently occurring subword:" % self.testing_iter)
                    if len(most_frequent_ngram) == 2:
                        print("%s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1])))
                    elif len(most_frequent_ngram) == 3:
                        print("%s    %s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]),  
                                                                                         get_str_token(most_frequent_ngram[2] )))        
                    else:
                        print("%s    %s    %s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]),  
                                                        get_str_token(most_frequent_ngram[2]), get_str_token(most_frequent_ngram[3]) ))
                    print("\n\nAdding to tokenizer vocab: ",  subword_for_most_frequent_ngram)
                ints_to_subwords_dict[self.next_index_available] = subword_for_most_frequent_ngram
                new_tokenizer_dict = update_tokenizer_dict( tokenizer_dict, most_frequent_ngram, self.next_index_available )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter: %d] UPDATED tokenizer dict:\n" % self.testing_iter)
                    for word in new_tokenizer_dict:
                        print("%s  =>  %s" % (word, str( [get_str_token(i) for i in new_tokenizer_dict[word]] )))
                self.next_index_available += 1
                return new_tokenizer_dict

            seed_value = 0
            random.seed(seed_value)
            os.environ['PYTHONHASHSEED'] = str(seed_value)
            print("\n\nTarget token vocabulary size: %s\n" % str(self.target_vocab_size))
            dir_textfiles =  self.corpus_dir
            ##  The dict defined in the next statement stores the mappings from the symbolic tokens to integers that represent 
            ##  them. For the number range 0 through 255, the mappings stored are those that are returned by calling chr() on 
            ##  the Unicode numbers between 0 and 255. Subsequently, as larger tokens are constructed by merging the "sub-word" 
            ##  tokens, we add those tokens and their associated numbers to this dict.   
            char_to_num_dict = { chr(num) :  num for num in range(256) }
            num_to_char_dict = { num : chr(num) for num in range(256) }
            ints_to_subwords_dict = { i : "" for i in range(256, self.target_vocab_size) }
            ##  I store all pairwise merges in the following array.  Each element of this array is a string 
            ##  that looks like  "str1 str2" where str1 and str2 are the two subwords that are to be merged together.
            merges = []                            
            vocab_word_to_merges_dict = {}                ## added in 1.1.1
            text = ""
            ##  Extract text data from the files. Note that using errors='ignore' may NOT be the right option for opening a file:  
            ##  https://stackoverflow.com/questions/45529507/unicodedecodeerror-utf-8-codec-cant-decode-byte-0x96-in-position-35-invalid
            if os.path.exists(dir_textfiles):
                    textfiles = glob.glob(dir_textfiles + "/*")
                    print("\n\nNumber of text files: ", len(textfiles))
                    for filedoc in textfiles:
                        if os.path.isfile(filedoc):
                            with open( filedoc, encoding='utf8', errors='ignore' ) as f:
                                text += f.read()
            if os.path.exists("tokenizer_outputs"):
                files = glob.glob("tokenizer_outputs/")
                for file in files:
                    if os.path.isfile(file):
                        os.remove(file)
                    else:
                        files = glob.glob(file + "/*")
                        list(map(lambda x: os.remove(x), files))  
            else:
                os.mkdir("tokenizer_outputs")

            #   print("\n\nlength of the text string: ", len(text))
            ##  We will store the merged char mappings for the new tokens in this dictionary
            merged_symbols_dict = {num : None for num in range(256, self.target_vocab_size) } 
            all_words = text.split()
            print("\n\nNumber of words in the corpus BEFORE filtering: ", len(all_words))
            ##  Added in Version 1.0.9:  Media articles downloaded from the newspaper websites frequently contain URL
            ##  strings that may be hundreds of characters long.  We get rid of all such strings by using 20 as the 
            ##  treshold for accepting a string for further proessing.  That is, we reject all strings that consist
            ##  of 20 or more characters. 
            all_words = [word for word in all_words if len(word) < 20]
            print("\n\nNumber of words in the corpus after filtering: ", len(all_words))
            print("\n\nfirst 100 entries in all_words: ", all_words[:100])
            ##  We need the word frequencies BECAUSE we need to find the most frequently occurring token pair 
            ##  in the corpus.  That is, for a given token pair, we need to know the number of words in which 
            ##  that pair occurs.
            words_with_counts = Counter(all_words)
            self.unique_words = list(set( all_words ))
            print("\n\nnumber of UNIQUE words: ", len(self.unique_words))
            print("\nfirst 100 UNIQUE words: ", self.unique_words[:100])
            if len(self.unique_words) < self.target_vocab_size // 4:
                sys.exit("\n\n\nEither your corpus size is too small or your target token vocabulary size is too large. Aborting!!!\n\n")
            word_tokens_dict =  { word : word_as_num_seq(word) for word in self.unique_words }         ##  Initialization of word_tokens_dict
            print("\n\nSTARTING ITERATIVE LEARNING OF THE MERGE RULES\n\nDEPENDING ON THE SIZE OF YOUR CORPUS, THIS COULD TAKE SEVERAL MINUTES.\n\n")
            for i in range(256): 
                ints_to_subwords_dict[i] = chr(i)           ## the char returned by the function chr(i) is the char under utf-8 encoding
            while self.next_index_available <= self.target_vocab_size:
                self.testing_iter += 1
                new_word_tokens_dict = find_best_ngram_and_update_word_tokens_dict( word_tokens_dict )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter = %d] Size of the tokenizer vocab: " % self.testing_iter,  self.next_index_available-1) 
                word_tokens_dict = new_word_tokens_dict
                if self.testing_iter % 5000 == 0:
                    FILE = open("ints_to_subwords_dictionary_" +  str(self.testing_iter) + ".txt", 'w')
                    for i in ints_to_subwords_dict: 
                        FILE.write("%d       =>       %s\n" % (i, ints_to_subwords_dict[i]))
                    ints_to_subwords_dict[self.target_vocab_size + 1] = "<UNK>"
                    subwords_to_ints_dict = {val : key for (key,val) in ints_to_subwords_dict.items()}
                    print("\n\n[testing_iter: %d] subwords_to_ints_dict: " % self.testing_iter, subwords_to_ints_dict)
                    print("\n\n[testing_iter: %d] merges array:" % self.testing_iter, merges)
                    vocab_and_merges =  {"version" : "1.0", 
                                         "truncation" : None,
                                         "padding" : None,
                                         "added_tokens" : [
                                              {"id" : self.target_vocab_size+1, 
                                               "content" : "<UNK>",
                                               "single_word": False,  
                                               "lstrip": False,
                                               "rstrip": False, 
                                               "normalized": False, 
                                               "special": True,
                                              },
                                         ],
                                         "normalizer": None,
                                         "pre_tokenizer": {
                                             "type": "Whitespace"
                                         },  
                                         "model" :  {"type": "BPE", "dropout" : None, "vocab" :  subwords_to_ints_dict,  "merges" : merges } }
                    with open(self.tokenizer_json_stem + str(self.testing_iter) + ".json", "w") as outfile:
                        json.dump(vocab_and_merges, outfile, indent=4)
            FILE = open("tokenizer_outputs/ints_to_subwords_dictionary_" +  str(self.testing_iter) + ".txt", 'w')
            for i in ints_to_subwords_dict: 
                FILE.write("%d       =>       %s\n" % (i, ints_to_subwords_dict[i]))
            ints_to_subwords_dict[self.target_vocab_size + 1] = "<UNK>"
            subwords_to_ints_dict = {val : key for (key,val) in ints_to_subwords_dict.items()}
            if self.debug:
                print("\n\nsubwords_to_ints_dict: ", subwords_to_ints_dict)
                print("\n\nmerges array:", merges)
            vocab_and_merges =  {"version" : "1.0", 
                                 "truncation" : None,
                                 "padding" : None,
                                 "added_tokens" : [
                                      {"id" : self.target_vocab_size+1, 
                                       "content" : "<UNK>",
                                       "single_word": False,  
                                       "lstrip": False,
                                       "rstrip": False, 
                                       "normalized": False, 
                                       "special": True,
                                      },
                                 ],
                                 "normalizer": None,
                                 "pre_tokenizer": {
                                     "type": "Whitespace"
                                 },  
                                 "model" :  {"type": "BPE", "dropout" : None, "vocab" :  subwords_to_ints_dict,  "merges" : merges } }
            with open(self.tokenizer_json_stem + str(len(subwords_to_ints_dict)) + ".json", "w") as outfile:
                json.dump(vocab_and_merges, outfile, indent=4)
            torch.save( ints_to_subwords_dict, "tokenizer_outputs/ints_to_subwords_dict.pt")
            torch.save( char_to_num_dict, "tokenizer_outputs/char_to_num_dict.pt")
            torch.save( num_to_char_dict, "tokenizer_outputs/num_to_char_dict.pt")
            torch.save( merges, "tokenizer_outputs/merges.pt")
            torch.save( self.unique_words, "tokenizer_outputs/unique_words.pt")
            torch.save( vocab_word_to_merges_dict, "tokenizer_outputs/vocab_word_to_merges_dict.pt")
            torch.save( self.next_index_available, "tokenizer_outputs/next_index_available.pt")
            print("\n\nFINISHED ITERATIVE LEARNING OF THE TOKENIZER VOCABULARY.\n\n")
            print("\n\nThe tokenizer JSON in the directory 'tokenizer_outputs'\n\n")
            return ints_to_subwords_dict, merges



        def post_training_cleanup(self):
            """
            The goal of this function to get rid of any superfluous tokens produced by the basic tokenizer training
            function "train_tokenizer()" defined for the TrainTokenizer class.  As also mentioned elsewhere in this
            file, given two tokens A and B, we consider A to be superfluous vis-a-vis B if the former is a 
            substring of the latter and if the the set of the unique corpus words that contain the two tokens are 
            exactly the same.
            """
            print("\n\n\n\nSTARTING POST-TRAINING CLEANUP OF THE LEARNED TOKEN VOCABULARY\n\n")
            if os.path.exists("cleaned_tokenizer_outputs"):
                files = glob.glob("cleaned_tokenizer_outputs/")
                for file in files:
                    if os.path.isfile(file):
                        os.remove(file)
                    else:
                        files = glob.glob(file + "/*")
                        list(map(lambda x: os.remove(x), files))  
            else:
                os.mkdir("cleaned_tokenizer_outputs")
            ints_to_subwords_dict   = torch.load("tokenizer_outputs/ints_to_subwords_dict.pt")
            merges             = torch.load("tokenizer_outputs/merges.pt")
            self.unique_words  = torch.load("tokenizer_outputs/unique_words.pt")
            vocab_word_to_merges_dict  = torch.load("tokenizer_outputs/vocab_word_to_merges_dict.pt")
            subwords_to_ints_dict = {val : key for (key,val) in ints_to_subwords_dict.items()}     
            print("\n\nsize of the token vocab before cleanup: ", len(subwords_to_ints_dict))               
            if self.debug:
                print("\nmerges before cleanup: ", merges)
                print("\nsize of merges: ", len(merges))
            relevant_ints_to_subwords_dict = {}           
            if self.debug:
                print("\n\n Some beginning and ending entries in ints_to_subwords_dict:\n")
                for i in range(10):
                    print("%d       =>       %s\n" % (i, ints_to_subwords_dict[i]))            
                print()
                for i in range(len(ints_to_subwords_dict)-10, len(ints_to_subwords_dict)):
                    print("%d       =>       %s\n" % (i, ints_to_subwords_dict[i]))            
            base_vocab = {}
            all_idx = sorted(ints_to_subwords_dict.keys())
            for idx in all_idx[:-1]:
                if self.debug:
                    print("\n\n\nstarting for idx: %d and with token1: %s and token2: %s" % 
                                                      (idx, ints_to_subwords_dict[idx], ints_to_subwords_dict[idx+1]))
                if len(  ints_to_subwords_dict[idx] ) == 1:
                    base_vocab[ ints_to_subwords_dict[idx] ]  = idx
                token1 = ints_to_subwords_dict[idx]
                token2 = ints_to_subwords_dict[idx+1]            
                unique1 = [word for word in self.unique_words if token1 in word]
                unique2 = [word for word in self.unique_words if token2 in word]
                if len(token1)<3 or len(token2)<3:
                    relevant_ints_to_subwords_dict[idx] = ints_to_subwords_dict[idx]
                    continue
                if len(token1)>1 and len(token2) >= 2 and not unique1 == unique2: 
                    relevant_ints_to_subwords_dict[idx] = ints_to_subwords_dict[idx]
            relevant_ints_to_subwords_dict[all_idx[-1]] = ints_to_subwords_dict[all_idx[-1]]
            relevant_subwords_to_ints_dict = {subword : intt for (intt, subword) in relevant_ints_to_subwords_dict.items()} 
            if self.debug:
                print("\n\nsize of base_vocab: ", len(base_vocab))
                print("\n\nsize of relevant_subwords_to_ints_dict: ", len(relevant_subwords_to_ints_dict))
            relevant_merges = []
            for v_item in relevant_subwords_to_ints_dict:
                for m_item in merges:
                    subword1,subword2 = m_item.split()
                    subword3 = subword1 + subword2
                    if not subword3 == v_item: continue
                    if  subword1 in relevant_subwords_to_ints_dict and subword2 in relevant_subwords_to_ints_dict \
                                                                               and subword3 in relevant_subwords_to_ints_dict:
                        assert subword1 in subwords_to_ints_dict and subword2 in subwords_to_ints_dict and subword3 in subwords_to_ints_dict
                        relevant_merges.append( m_item )
            if self.debug:
                print("\n\nHere is relevant_merges: ")
                print(relevant_merges)
                print("\nsize of relevant_merges: ", len(relevant_merges))
            new_subwords_to_ints_dict = copy.deepcopy(base_vocab)
            idx = len(base_vocab)
            for item in relevant_merges:
                subword1,subword2 = item.split()
                new_subwords_to_ints_dict[subword1] = idx
                idx += 1 
                new_subwords_to_ints_dict[subword2] = idx
                idx += 1 
                new_subwords_to_ints_dict[subword1+subword2] = idx
                idx += 1 
            new_subwords_to_ints_dict["<UNK>"] =  idx
            print("\nsize of the token vocab after cleanup: ", len(new_subwords_to_ints_dict))
            if self.debug:
                print("\n\ntoken vocab after cleanup: ", new_subwords_to_ints_dict)
            vocab_and_merges =  {"version" : "1.0", 
                                 "truncation" : None,
                                 "padding" : None,
                                 "added_tokens" : [
                                      {"id" : self.target_vocab_size+1, 
                                       "content" : "<UNK>",
                                       "single_word": False,  
                                       "lstrip": False,
                                       "rstrip": False, 
                                       "normalized": False, 
                                       "special": True,
                                      },
                                 ],
                                 "normalizer": None,
                                 "pre_tokenizer": {
                                     "type": "Whitespace"
                                 },  
                                 "model" :  {"type": "BPE", "dropout" : None, "vocab" :  new_subwords_to_ints_dict,  "merges" : relevant_merges } }

            with open(self.cleaned_tokenizer_json_stem + str(len(new_subwords_to_ints_dict)) + ".json", "w") as outfile:
                json.dump(vocab_and_merges, outfile, indent=4)
            torch.save( relevant_merges, "cleaned_tokenizer_outputs/relevant_merges.pt")
            print("\n\n\nFinished cleaning up the token vocabulary.")
            print("\nThe tokenizer JSON you need is in the directory 'cleaned_tokenizer_outputs'\n\n")



        def extend_tokenizer_with_additional_training(self, tokenizer_json):
            """
            Since tokenizer training is CPU intensive, it can take quite a bit of time to create a tokenizer, with the
            length of time depending on both the size of the corpus and the target size for the token vocab.  And, it 
            is not uncommon that as you are staring at the intermediate results during tokenizer training, you wish 
            you had gone for a larger target size for the token vocabulary.  The purpose of this function is to 
            address this need.  After you have finished training the tokenizer using the previous function, you can 
            invoke this function for a larger target vocab.  To facilitate this function picking up the tokenizer 
            training where the previous function left off, I have modified the previous function a bit in order to 
            save the data structures that this function loads in order to continue the training.
            """
            def word_as_num_seq(word):
                for char in list(word):
                    if char not in char_to_num_dict:
                        char_to_num_dict[char] = self.next_index_available
                        ints_to_subwords_dict[ self.next_index_available ] = char
                        self.next_index_available += 1       
                return [char_to_num_dict[char] for char in list(word) ]
            
            def get_str_token( num ):
                """
                Note that ints_to_subwords_dict is what becomes the vocab eventually.  We make the
                conversion by reversing the <key,num> pairs in ints_to_subwords_dict.
                """
                if num in num_to_char_dict:
                    return num_to_char_dict[num]
                elif num in ints_to_subwords_dict:
                    return ints_to_subwords_dict[num]
                else:
                    sys.exit("\n\n[get_str_token]  ints_to_subwords_dict has no merge rule for the int token %d\n\n" % num)
            
            def subword_for_num_seq( num_seq ):
                subword = ""
                for num in num_seq:
                    if num in num_to_char_dict:
                        subword += chr(num)
                    elif num in ints_to_subwords_dict:
                        subword += ints_to_subwords_dict[num]
                    else:
                        sys.exit("\n\n[subword_for_num_seq] ints_to_subwords_dict has no merge rule for the int token %d\n\n" % num)
                return subword
            
            def update_tokenizer_dict( tokenizer_dict, most_frequent_pair, new_token_as_num ):
                new_tokenizer_dict = {word : [] for word in tokenizer_dict}
                for word in tokenizer_dict:
                    str_rep = ",".join(str(i) for i in tokenizer_dict[word])
                    to_be_replaced_pair =  r"\b" +  ",".join(str(i) for i in most_frequent_pair) + r"\b"
                    replacement = str(new_token_as_num) 
                    output_str= re.sub(to_be_replaced_pair, replacement, str_rep)
                    new_tokenizer_dict[word]  =  [int(i) for i in output_str.split(",")]
                return new_tokenizer_dict
            
            
            def find_best_ngram_and_update_word_tokens_dict(tokenizer_dict):
                all_consec_pairs_dict = { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:] ) ) for word in tokenizer_dict }
                all_consec_triples_dict =   { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:],  tokenizer_dict[word][2:] ) ) 
                                                                                                                     for word in tokenizer_dict }
                all_consec_quads_dict   =   { word : list( zip( tokenizer_dict[word], tokenizer_dict[word][1:],  tokenizer_dict[word][2:], 
                                                                                        tokenizer_dict[word][3:] ) ) for word in tokenizer_dict }   
                all_consec_all_ngrams_dict = {}
                for word in all_consec_pairs_dict:
                    if word in all_consec_triples_dict and  word in all_consec_quads_dict:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word] + all_consec_triples_dict[word] + all_consec_quads_dict[word]
                    elif word in all_consec_triples_dict:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word] + all_consec_triples_dict[word]
                    else:
                        all_consec_all_ngrams_dict[word]  =  all_consec_pairs_dict[word]
                all_consec_all_ngrams_dict  =   {word : all_consec_all_ngrams_dict[word] for word in all_consec_all_ngrams_dict 
                                                                                                      if len(all_consec_all_ngrams_dict[word]) > 0}
                most_frequent_ngram = list(Counter( list( itertools.chain(*all_consec_all_ngrams_dict.values()) ) ).keys()) [0]
                string_for_merges_array = "%s %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]))
                merges.append( string_for_merges_array )
                subword_for_most_frequent_ngram  =  subword_for_num_seq( most_frequent_ngram )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter: %d] Will merge the following subwords for the new most frequently occurring subword:" % self.testing_iter)
                    if len(most_frequent_ngram) == 2:
                        print("%s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1])))
                    elif len(most_frequent_ngram) == 3:
                        print("%s    %s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]),  
                                                                                         get_str_token(most_frequent_ngram[2] )))        
                    else:
                        print("%s    %s    %s    %s" % (get_str_token(most_frequent_ngram[0]), get_str_token(most_frequent_ngram[1]),  
                                                        get_str_token(most_frequent_ngram[2]), get_str_token(most_frequent_ngram[3]) ))
                    print("\n\nAdding to tokenizer vocab: ",  subword_for_most_frequent_ngram)
                ints_to_subwords_dict[self.next_index_available] = subword_for_most_frequent_ngram
                new_tokenizer_dict = update_tokenizer_dict( tokenizer_dict, most_frequent_ngram, self.next_index_available )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter: %d] UPDATED tokenizer dict:\n" % self.testing_iter)
                    for word in new_tokenizer_dict:
                        print("%s  =>  %s" % (word, str( [get_str_token(i) for i in new_tokenizer_dict[word]] )))
                self.next_index_available += 1
                return new_tokenizer_dict

            print("\n\n\nYou should run this script ONLY AFTER you have run the 'train_tokenizer.py' script in this directory.\n\n\n")
            if os.path.exists("extended_tokenizer_outputs"):
                files = glob.glob("extended_tokenizer_outputs/")
                for file in files:
                    if os.path.isfile(file):
                        os.remove(file)
                    else:
                        files = glob.glob(file + "/*")
                        list(map(lambda x: os.remove(x), files))  
            else:
                os.mkdir("extended_tokenizer_outputs")
            seed_value = 0
            random.seed(seed_value)
            os.environ['PYTHONHASHSEED'] = str(seed_value)
            dir_textfiles =  self.corpus_dir
            self.next_index_available  =  torch.load("tokenizer_outputs/next_index_available.pt")
            print("\n\n[FOR EXTENDING THE TOKENIZER]  next_index_available: ", self.next_index_available)
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file= tokenizer_json)
            FILE = open(tokenizer_json)
            tokenizer_dict   =    json.load( FILE ) 
            char_to_num_dict =    torch.load( "tokenizer_outputs/char_to_num_dict.pt")
            num_to_char_dict =    torch.load( "tokenizer_outputs/num_to_char_dict.pt")
            ints_to_subwords_dict =    torch.load( "tokenizer_outputs/ints_to_subwords_dict.pt")
            merges           =    torch.load( "tokenizer_outputs/merges.pt")
            text = ""
            if os.path.exists(dir_textfiles):
                    textfiles = glob.glob(dir_textfiles + "/*")
                    print("\n\nNumber of text files: ", len(textfiles))
                    for filedoc in textfiles:
                        if os.path.isfile(filedoc):
                            with open( filedoc, encoding='utf8', errors='ignore' ) as f:
                                text += f.read()
            all_words = text.split()
            all_words = [word for word in all_words if len(word) < 20]
            ##  We need the word frequencies BECAUSE we need to find the most frequently occurring token pair 
            ##  in the corpus.  That is, for a given token pair, we need to know the number of words in which 
            ##  that pair occurs.
            words_with_counts = Counter(all_words)
            self.unique_words = list(set( all_words ))
            word_tokens_dict =  { word : word_as_num_seq(word) for word in self.unique_words }        
            print("\n\nIterative learning of the merge rules:\n\nDEPENDING ON THE SIZE OF YOUR CORPUS, THIS COULD TAKE SEVERAL MINUTES.\n\n")
            while self.next_index_available <= self.target_vocab_size:
                self.testing_iter += 1
                new_word_tokens_dict = find_best_ngram_and_update_word_tokens_dict( word_tokens_dict )
                if self.testing_iter % 100 == 0:
                    print("\n\n[testing_iter = %d] Size of the tokenizer vocab: " % self.testing_iter,  self.next_index_available-1) 
                word_tokens_dict = new_word_tokens_dict
                if self.testing_iter % 5000 == 0:
                    FILE = open("extended_tokenizer_outputs/ints_to_subwords_dictionary_" +  str(self.testing_iter) + ".txt", 'w')
                    for i in ints_to_subwords_dict: 
                        FILE.write("%d       =>       %s\n" % (i, ints_to_subwords_dict[i]))
                    ints_to_subwords_dict[self.target_vocab_size + 1] = "<UNK>"
                    subwords_to_ints_dict = {val : key for (key,val) in ints_to_subwords_dict.items()}
                    print("\n\n[testing_iter: %d] subwords_to_ints_dict: " % self.testing_iter, subwords_to_ints_dict)
                    print("\n\n[testing_iter: %d] merges array:" % self.testing_iter, merges)
                    vocab_and_merges =  {"version" : "1.0", 
                                         "truncation" : None,
                                         "padding" : None,
                                         "added_tokens" : [
                                              {"id" : self.target_vocab_size+1, 
                                               "content" : "<UNK>",
                                               "single_word": False,  
                                               "lstrip": False,
                                               "rstrip": False, 
                                               "normalized": False, 
                                               "special": True,
                                              },
                                         ],
                                         "normalizer": None,
                                         "pre_tokenizer": {
                                             "type": "Whitespace"
                                         },  
                                         "model" :  {"type": "BPE", "dropout" : None, "vocab" :  subwords_to_ints_dict,  "merges" : merges } }
                    with open(self.extended_tokenizer_json_stem + str(self.testing_iter) + ".json", "w") as outfile:
                        json.dump(vocab_and_merges, outfile, indent=4)
            FILE = open( "extended_tokenizer_outputs/ints_to_subwords_dictionary_" +  str(self.testing_iter) + ".txt", 'w')
            for i in ints_to_subwords_dict: 
                FILE.write("%d       =>       %s\n" % (i, ints_to_subwords_dict[i]))
            ints_to_subwords_dict[self.target_vocab_size + 1] = "<UNK>"
            subwords_to_ints_dict = {val : key for (key,val) in ints_to_subwords_dict.items()}
            print("\n\nvocab: ", subwords_to_ints_dict)
            print("\n\nmerges array:", merges)
            vocab_and_merges =  {"version" : "1.0", 
                                 "truncation" : None,
                                 "padding" : None,
                                 "added_tokens" : [
                                      {"id" : self.target_vocab_size+1, 
                                       "content" : "<UNK>",
                                       "single_word": False,  
                                       "lstrip": False,
                                       "rstrip": False, 
                                       "normalized": False, 
                                       "special": True,
                                      },
                                 ],
                                 "normalizer": None,
                                 "pre_tokenizer": {
                                     "type": "Whitespace"
                                 },  
                                 "model" :  {"type": "BPE", "dropout" : None, "vocab" :  subwords_to_ints_dict,  "merges" : merges } }
            with open(self.extended_tokenizer_json_stem + str(len(subwords_to_ints_dict)) + ".json", "w") as outfile:
                json.dump(vocab_and_merges, outfile, indent=4)
            torch.save( ints_to_subwords_dict, "extended_tokenizer_outputs/ints_to_subwords_dict.pt")
            torch.save( char_to_num_dict, "extended_tokenizer_outputs/char_to_num_dict.pt")
            torch.save( num_to_char_dict, "extended_tokenizer_outputs/num_to_char_dict.pt")
            torch.save( merges, "extended_tokenizer_outputs/merges.pt")


    ###%%%
    #############################################################################################################################
    #############################  Start Definition of Inner Class ArticleDatasetWithBufferedContext  ###########################

    class ArticleDatasetWithBufferedContext(Dataset):    
        """
        This class supplies the 'foundational' dataloader for training. When using the PyTorch Lightning 
        module for for multi-GPU training, this dataloader is routed through Lightning's LightningDataModule 
        class as you will see later in this code file.  Lightning requires its dataloaders to be Python 
        generators.

        The parameter 'context_window_size' is the number of fresh tokens that the dataloader must supply in
        each training iteration.  And the parameter 'context_buffer_size' is the number of trailing tokens
        in the previous batch that are prepended to the fresh tokens in the current batch. The number of 
        tokens that the transformer network sees is the sum of these two sizes.  

        The sum of context_window_size and context_buffer_size is referred to as 'max_seq_length' in the 
        code.
        """
        def __init__(self, gpt, tokenizer_json, context_window_size, context_buffer_size=7, articles_dir='saved_articles_dir'):
            super(babyGPT.ArticleDatasetWithBufferedContext, self).__init__()
            if os.path.exists(articles_dir): 
                num_articles = len(glob.glob(articles_dir + "/*")) 
                if gpt.verify_text_corpus:
                    if num_articles == 0:
                        sys.exit("\n\nAborting --- You have no articles in the articles directory.  You may need to first use the ArticleGatherer")
                    ans = input("\n\nYou have %d articles in the articles directory. Continue? Enter 'y' if yes: " % num_articles)
                    ans = ans.strip()
                    if ans != ('y' or 'yes'): 
                        print("\n\nPlease run the 'run_gatherer()' function to gather the news articles.\n\n")
            else:
                sys.exit("\n\nAborting --- Your articles directory %s does not exist." % articles_dir)
            print("\n\nThe Dataloader will be applied to the previously collected trove of articles in %s." % articles_dir)
            print()
            self.dir_collected_articles = articles_dir
            self.num_articles = num_articles
            self.context_buffer_size = context_buffer_size
            ## The file named below must be a json file created by a tokenizer training routine:
            self.tokenizer_json = tokenizer_json                       
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.tokenizer_json)
            FILE = open(self.tokenizer_json)    
            tokenizer_dict =  json.load( FILE ) 
            self.batch_size = gpt.batch_size
            self.context_window_size = context_window_size
            self.inverse_lookup  =  {v:k for k,v in tokenizer_dict['model']['vocab'].items()}  
            self.articles = []
            self.articles_for_batch_instances = []
            self.encoded_streams = {}              ## A dict whose keys are batch instance indexes            
            self.all_encoded_streams  =   []       ## A list of the values in the above dict
            self.iteration_index = 0               ## This value is reset to 0 at the beginning of each new epoch
            self.epoch_index = 0
            self.datastreams_initialized = False
            ## Added in Version 1.0.8  [These were previously called by initialize_tokenized_data_streams()
            self.articles = glob.glob(self.dir_collected_articles + "/*")               
            self.generate_article_sequences_for_batch_instances()
            self.generate_token_streams_for_batch_instances()


        def generate_article_streams(self):
            debug = False
            def gen(container):
                j = 0
                while j < len(container):
                    yield container[j]
                    j += 1
            random.shuffle(self.articles)
            self.articles_for_batch_instances = [self.articles[i:i+len(self.articles)//self.batch_size] for i in range(self.batch_size)]
            self.encoded_streams =  []
            ## Create a stream of encoding for each batch instance
            for i in  range(self.batch_size):
                article_gen = gen( self.articles_for_batch_instances[i] )
                encoded_stream = [] 
                for article in article_gen:
                    if article is None: break
                    FILE = open(article)
                    text = FILE.read()
                    ## next 3 statements added in 1.0.9:
                    all_words = text.split()
                    all_words = [word for word in all_words if len(word) < 20]
                    text = ' '.join(all_words)
                    if debug:
                        encoded = self.tokenizer.encode(text)
                        print("\n\n\ntext in article: ", text)
                        print("after tokenization and encoding: ", encoded)
                        the_tokens = [self.inverse_lookup[code] for code in encoded]
                        print("the individual tokens: ", the_tokens)
                    encoded_stream += self.tokenizer.encode(text)
                self.encoded_streams.append( encoded_stream )
    

        def generate_article_sequences_for_batch_instances(self):
            """
            "equalization" here means that we want all the streams AS EQUAL IN LENGTH AS POSSIBLE
            based on N different attempts at article randomization.  Highly unequal stream lengths 
            can make GPT learning inefficient --- and sometimes impossible.
            """
            debug = False
            ## We need to find the total number of tokens in all the articles in our corpus.  Subsequently,
            ## when we partition the corpus into sub-corpora, with one sub-corpus for each batch instance,
            ## we want to make sure that the total number of tokens available for the token-stream created
            ## for each batch instance is roughly the same.
            article_sizes = { article : None for article in self.articles }  ## size is measured in terms of the number of tokens
            master_article_gen = gen(self.articles)
            total_num_tokens = 0 
            for article in master_article_gen:
                FILE = open(article)
                text = FILE.read()
                article_tokens = self.tokenizer.encode( text )
                article_sizes[article] = len(article_tokens) 
                total_num_tokens += len(article_tokens)
            if self.epoch_index == 0 :
                # print("\n\n\narticle sizes: ", article_sizes)
                print("total_num_tokens: ", total_num_tokens)

            ##  Now we want to assign articles to each batch instance in such a way that the total number
            ##  of tokens assigned to a batch instance is approximately the same for batch instances. I am
            ##  going to use the followings dicts for this logic:
            num_tokens_per_batch_instance = total_num_tokens // self.batch_size
            article_sequence_for_batch_instance = {i : [] for i in range(self.batch_size)}           ## The sub-corpora of articles
            char_stream_size_for_batch_instance = {i : 0 for i in range(self.batch_size)}          ## The token stream for each sub-corpus

            ##  Now we are ready to create a sub-corpus for each batch instance. Each sub-corpus will eventually 
            ##  be turned into a token stream.  The epoch-to-epoch randomization of the input data would consist
            ##  of randomizing the sequence of articles (meaning, the order in which the articles appear) in
            ##  each sub-corpus.
            for article in article_sizes:
                ##  This is a variant of the heuristic algorithms used commonly for solving the combinatorial NP-Hard BIN 
                ##  PACKING Optimization problem in which the object are placed in unit-sized bins so as to minimize the
                ##  bins used.  The heuristic I have used here is to assign an article to that sub-corpus that currently
                ##  has the least total number of tokens in it. REMEMBER we measure the size of an article in terms of the 
                ##  number of tokens needed for that article.
                smallest_idx =  (sorted(char_stream_size_for_batch_instance, key=char_stream_size_for_batch_instance.get ))[0]
                article_sequence_for_batch_instance[smallest_idx].append(article)
                char_stream_size_for_batch_instance[smallest_idx] += article_sizes[article]
            ##  Let's now check we did a good job of roughly equalizing the number of tokens for each sub-corpus:
            for i in  range(self.batch_size):
                total_num_tokens = 0 
                article_gen = gen(article_sequence_for_batch_instance[i])
                for article in article_gen:
                    FILE = open(article)
                    text = FILE.read()
                    article_tokens = self.tokenizer.encode( text )
                    article_sizes[article] = len(article_tokens) 
                    total_num_tokens += len(article_tokens)
         
            self.article_sequence_for_batch_instance = article_sequence_for_batch_instance

        def generate_token_streams_for_batch_instances(self):
            debug = False 
            article_sequence_for_batch_instance  = self.article_sequence_for_batch_instance
            for seq_idx in article_sequence_for_batch_instance:
                random.shuffle( article_sequence_for_batch_instance[seq_idx] )          ## randomization at the beginning of each epoch
            ## Create a stream of encoding for each batch instance
            self.encoded_streams =  {i : [] for i in range(self.batch_size)}
            for i in  range(self.batch_size):
                article_gen = gen(article_sequence_for_batch_instance[i])
                for article in article_gen:
                    FILE = open(article)
                    text = FILE.read()
                    ## Change made on Jan 29, 2025. Insert underscore between the words to help out with the detokenization step:
                    all_words = text.split()  
                    all_words = [word + " _" if re.search(r'.*[\w]$', word) else word for word in all_words] 
                    text = ' '.join(all_words)
                    article_tokens = self.tokenizer.encode( text )
                    self.encoded_streams[i] += article_tokens
            ## Now let's check the difference in length between the longest batch-instance stream
            ## and the shortest batch-instance stream:
            self.all_encoded_streams = list(self.encoded_streams.values())
            shortest_encoded_stream = min(self.all_encoded_streams, key=lambda x: len(x))
            longest_encoded_stream = max(self.all_encoded_streams, key=lambda x: len(x))
            stream_len_disparity =  len(longest_encoded_stream)  -  len(shortest_encoded_stream) 
            self.num_batches = len(shortest_encoded_stream) // self.context_window_size
            print("\n\nlength of the shortest stream: ", len(shortest_encoded_stream))
            print("length of the longest stream: ", len(longest_encoded_stream))
            print("value of stream_len_disparity: ", stream_len_disparity)
            print("number of training iterations per epoch [approximate]: ",  len(shortest_encoded_stream) // self.context_window_size)

        def initialize_tokenized_data_streams(self):
#            if self.datastreams_initialized == False:
            self.articles = glob.glob(self.dir_collected_articles + "/*")               
            self.generate_article_sequences_for_batch_instances()
            self.generate_token_streams_for_batch_instances()
            self.datastreams_initialized = True

        def dataloader_for_buffered_context(self, how_many):
            """
            This is the dataloader that was used in Version 1.0.7 of babyGPT.

            In babyGPT version 1.0.8, I made the class ArticleDatasetWithBufferedContext a subclass of the 
            PyTorch class 'torch.utils.data.Dataset'.  That requires to define __len__() and __getitem__() for the
            class -- you will see these after the end of the definition of the current function.

            This is the dataloader supplied by the ArticleDatasetWithBufferedContext class.  As I have demonstrated
            elsewhere, the output of this dataloader is fed into PyTorch Lightning's LightningDataModule class for
            multi-gpu training. 

            The parameter "how_many" shown above means the size of the context_window_size that is specified in the 
            call to the constructor of ArticleDatasetWithBufferedContext. 

            This function returns a batch of token sequences on each call.  A batch is constructing by pulling the token sequences 
            for each batch instance from the 'batch_size' number of token streams created in the constructor of the 'Ddataloader'
            class. When that process gets too close the end of the shortest of the 'batch_size' number of streams, the articles 
            are randomized again for assignment to the individual batch-instance streams.

            The variable   self.iteration_index  keeps track of where the downloader is in each batch-instance stream as feed data
            one batch at a time into the Transformer.
            """
            debug = False
            batch_size = self.batch_size
            context_window_size = how_many
            cws_minus_one = context_window_size - 1
            codes_for_SOS = [89, 90, 91, 92, 93, 94, 96, 97, 98]

            if any( len( self.all_encoded_streams[i][self.iteration_index*cws_minus_one : ] )  < cws_minus_one for i in range(batch_size) ):
                self.epoch_index += 1
                print("\n\nStarting epoch: %d\n" % (self.epoch_index + 1))
                self.iteration_index = 0

            ## self.iteration_index == 0  means we are starting a new epoch
            if self.datastreams_initialized and self.iteration_index == 0:
                self.articles = glob.glob(self.dir_collected_articles + "/*")               
                self.generate_article_sequences_for_batch_instances()
                self.generate_token_streams_for_batch_instances()

            out = np.zeros(shape=(batch_size, context_window_size), dtype=int)

            for i in range(batch_size):
                out[i,1:] =  self.all_encoded_streams[i][self.iteration_index*cws_minus_one :  (self.iteration_index+1) * cws_minus_one]
                out[i,0] = 89                                ## for the SOS token
            self.iteration_index  += 1
            return out


        def test_dataloader(self, how_many):
            data = self.dataloader_for_buffered_context(how_many)
            print("\n\n\nshape of the data returned by the dataloader: ", data.shape)
            print("\n\ndata returned by the dataloader:")
            print(data)
            tokens = [[self.inverse_lookup[code] for code in data[i]] for i in range(self.batch_size)]
            print(tokens)
            
            data = self.dataloader_for_buffered_context(how_many)
            print("\n\n\nshape of the data returned by the dataloader: ", data.shape)
            print("\n\ndata returned by the dataloader:")
            print(data)
            tokens = [[self.inverse_lookup[code] for code in data[i]]  for i in range(self.batch_size)]
            print(tokens)
            

        def display_token_vocab(self):  
            for code in self.inverse_lookup:
                print("%d        =>       %s" % (code , str( self.inverse_lookup[code] ) ) )

        def __len__(self):
            return self.num_batches - 1

        def __getitem__(self, idx):
            cws_minus_one = self.context_window_size - 1
            codes_for_SOS = [89, 90, 91, 92, 93, 94, 96, 97, 98]
            if idx < len(self):
                out = np.zeros(shape=(self.batch_size, self.context_window_size), dtype=int)
                for i in range(self.batch_size):
                    out[i,1:] =  self.all_encoded_streams[i][idx*cws_minus_one :  (idx+1) * cws_minus_one]
                    out[i,0] = codes_for_SOS[0]
                return out
            else:
                self.epoch_index += 1       
                self.initialize_tokenized_data_streams()
                raise StopIteration


    ###%%%
    #############################################################################################################################
    ########################################  Start Definition of Inner Class TransformerFG  ####################################

    class TransformerFG(nn.Module):             
        """
        This I have borrowed from the DLStudio's Transformers module.  "FG" stands for "First Generation" --- which is 
        the Transformer as originally proposed by Vaswani et al.
        """
        def __init__(self, max_seq_length, embedding_size, tokenizer_json, num_warmup_steps=None, optimizer_params=None):
            super(babyGPT.TransformerFG, self).__init__()
            self.max_seq_length = max_seq_length
            self.embedding_size = embedding_size
            self.num_warmup_steps = num_warmup_steps
            self.optimizer_params = optimizer_params
            self.tokenizer_json = tokenizer_json                       
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.tokenizer_json)
            FILE = open(self.tokenizer_json)    
            tokenizer_dict =  json.load( FILE ) 
            self.inverse_lookup  =  {v:k for k,v in tokenizer_dict['model']['vocab'].items()}  
            self.vocab_size = self.tokenizer.vocab_size
    
        def sentence_with_words_to_ints(self, sentences, lang):
            sentence_to_ints = torch.ones(len(sentences), self.max_seq_length, dtype=torch.long)
            for i in range(len(sentences)):
                words = sentences[i].split(' ')
                for j,word in enumerate(words):
                    sentence_to_ints[i,j] = self.en_vocab_dict[word] if lang=="en" else self.es_vocab_dict[word]
            return sentence_to_ints
    
    class EmbeddingGenerator(nn.Module):
        def __init__(self, xformer, embedding_size):
            super(babyGPT.EmbeddingGenerator, self).__init__()
            tokenizer = PreTrainedTokenizerFast(tokenizer_file=xformer.tokenizer_json)
            self.vocab_size =  xformer.vocab_size
            self.embedding_size = embedding_size                                             
            self.max_seq_length = xformer.max_seq_length                                                     
            self.embed = nn.Embedding(self.vocab_size, embedding_size)
 
        def forward(self, sentence_tensor):                                                                 
            ## Let's say your batch_size is 4 and that each sentence has a max_seq_length of 10.
            ## The sentence_tensor argument will now be of shape [4,10].  If the embedding size is
            ## is 512, the following call will return a tensor of shape [4,10,512)
            word_embeddings = self.embed(sentence_tensor)
            position_coded_word_embeddings = self.apply_positional_encoding( word_embeddings )
            return position_coded_word_embeddings

        def apply_positional_encoding(self, sentence_tensor):
            position_encodings = torch.zeros_like( sentence_tensor ).float()
            ## Calling unsqueeze() with arg 1 causes the "row tensor" to turn into a "column tensor"
            ##    which is needed in the products shown below. We create a 2D pattern by 
            ##    taking advantage of how PyTorch has overloaded the definition of the infix '*' 
            ##    tensor-tensor multiplication operator.  It in effect creates an output-product of
            ##    of what is essentially a column vector with what is essentially a row vector.
            word_positions = torch.arange(0, self.max_seq_length).unsqueeze(1)            
            div_term =  1.0 / (100.0 ** ( 2.0 * torch.arange(0, self.embedding_size, 2) / float(self.embedding_size) ))
            position_encodings[:, :, 0::2] =  torch.sin(word_positions * div_term)                             
            position_encodings[:, :, 1::2] =  torch.cos(word_positions * div_term)                             
            return sentence_tensor + position_encodings

    ###%%%
    #######################################################################################################################
    ###################################  Self Attention Code for TransformerFG  ###########################################

    class SelfAttention(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_atten_heads):
            super(babyGPT.SelfAttention, self).__init__()
            self.max_seq_length = xformer.max_seq_length                                                     
            self.embedding_size = xformer.embedding_size
            self.num_atten_heads = num_atten_heads
            self.qkv_size = self.embedding_size // num_atten_heads
            self.attention_heads_arr = nn.ModuleList( [babyGPT.AttentionHead(self.max_seq_length, 
                                    self.qkv_size, num_atten_heads)  for _ in range(num_atten_heads)] )           

        def forward(self, sentence_tensor):                                                                       
            concat_out_from_atten_heads = torch.zeros( sentence_tensor.shape[0], self.max_seq_length, 
                                                                  self.num_atten_heads * self.qkv_size,
                                                                  device=sentence_tensor.device,
                                                                  dtype=sentence_tensor.dtype)#.float()
            for i in range(self.num_atten_heads):                                                                 
                sentence_embed_slice = sentence_tensor[:, :, i * self.qkv_size : (i+1) * self.qkv_size]
                concat_out_from_atten_heads[:, :, i * self.qkv_size : (i+1) * self.qkv_size] =          \
                                                               self.attention_heads_arr[i](sentence_embed_slice)   
            return concat_out_from_atten_heads


    class AttentionHead(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self,  max_seq_length, qkv_size, num_atten_heads):
            super(babyGPT.AttentionHead, self).__init__()
            self.qkv_size = qkv_size
            self.max_seq_length = max_seq_length
            self.WQ =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.WK =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.WV =  nn.Linear( self.qkv_size, self.qkv_size )                                                      
            self.softmax = nn.Softmax(dim=-1)                                                                          

        def forward(self, sent_embed_slice):           ## sent_embed_slice == sentence_embedding_slice                
            Q = self.WQ( sent_embed_slice )                                                                           
            K = self.WK( sent_embed_slice )                                                                           
            V = self.WV( sent_embed_slice )                                                                           
            A = K.transpose(2,1)                                                                                      
            QK_dot_prod = Q @ A                                                                                       
            rowwise_softmax_normalizations = self.softmax( QK_dot_prod )                                              
            Z = rowwise_softmax_normalizations @ V                                                                    
            coeff = 1.0 / math.sqrt(self.qkv_size)  
            Z = coeff * Z                                                                          
            return Z


    ###%%%
    #######################################################################################################################
    #########################################  Basic Decoder Class for TransformerFG  #####################################

    class BasicDecoderWithMasking(nn.Module):
        """
        Borrowed from the Transformers module of DLStudio
        """  
        def __init__(self, xformer, num_atten_heads, masking=True):
            super(babyGPT.BasicDecoderWithMasking, self).__init__()
            self.masking = masking
            self.embedding_size = xformer.embedding_size                                             
            self.max_seq_length = xformer.max_seq_length                                                     
            self.num_atten_heads = num_atten_heads
            self.qkv_size = self.embedding_size // num_atten_heads
            self.self_attention_layer = babyGPT.SelfAttention(xformer, num_atten_heads)
            self.norm1 = nn.LayerNorm(self.embedding_size)
            self.norm2 = nn.LayerNorm(self.embedding_size)
            ## What follows are the linear layers for the FFN (Feed Forward Network) part of a BasicDecoder
            self.W1 =  nn.Linear( self.embedding_size, 4 * self.embedding_size )
            self.W2 =  nn.Linear( 4 * self.embedding_size, self.embedding_size ) 
            self.norm3 = nn.LayerNorm(self.embedding_size)

        def forward(self, sentence_tensor, mask):   
            masked_sentence_tensor = self.apply_mask(sentence_tensor, mask)
            Z_concatenated = self.self_attention_layer(masked_sentence_tensor)
            Z_out = self.norm1(Z_concatenated + masked_sentence_tensor)
            ## for FFN:
            basic_decoder_out =  nn.ReLU()(self.W1( Z_out.view( sentence_tensor.shape[0], self.max_seq_length, -1) ))                  
            basic_decoder_out =  self.W2( basic_decoder_out )                                                    
            basic_decoder_out = basic_decoder_out.view(sentence_tensor.shape[0], self.max_seq_length, self.embedding_size )
            basic_decoder_out =  basic_decoder_out  + Z_out 
            basic_decoder_out = self.norm3( basic_decoder_out )
            return basic_decoder_out

        def apply_mask(self, sentence_tensor, mask):
            out = torch.zeros_like(sentence_tensor)
            out[:,:len(mask),:] = sentence_tensor[:,:len(mask),:] 
            return out    


    ###%%%
    #######################################################################################################################
    ######################################  MasterDecoder Class for TransformerFG #########################################

    class MasterDecoderWithMasking(L.LightningModule):
        """
        This class was borrowed initially from the Transformers module of the DLStudio platform.  Subsequently, its 
        definition was significantly expanded to fulfill the constraints imposed by the PyTorch Lightning API.
        For information regarding the operation of this class, please visit the website for DLStudio at Purdue.
        """  
        def __init__(self, xformer, num_basic_decoders, num_atten_heads, context_window_size, context_buffer_size, batch_size, masking=True):
            super(babyGPT.MasterDecoderWithMasking, self).__init__()
            self.automatic_optimization = False
            self.xformer = xformer
            self.masking = masking
            self.max_seq_length = xformer.max_seq_length
            self.embedding_size = xformer.embedding_size
            self.vocab_size = xformer.vocab_size                                             
            self.basic_decoder_arr = nn.ModuleList([babyGPT.BasicDecoderWithMasking( xformer,
                                                    num_atten_heads, masking) for _ in range(num_basic_decoders)])  
            ##  Need the following layer because we want the prediction of each target word to be a probability 
            ##  distribution over the target vocabulary. The conversion to probs would be done by the criterion 
            ##  nn.CrossEntropyLoss in the training loop:
            self.out = nn.Linear(self.embedding_size, self.vocab_size)                                          
            self.n_warmup_steps = 4000
            self.context_window_size = context_window_size
            self.context_buffer_size = context_buffer_size
#            self.prev_seq_logprobs = torch.ones(batch_size, xformer.vocab_size, dtype=torch.float)
            self.register_buffer("prev_seq_logprobs",torch.ones(batch_size, xformer.vocab_size, dtype=torch.float)) 
            self.accum_times = []
            self.start_time = time.perf_counter()
            self.training_loss_tally  = []
            self.running_loss = 0.0
            self.training_iter = 0
            self.epoch_index = 0
            self.batch_size = batch_size
            self.loss_normed  =  self.predicted_word_logprobs =  self.token_sequences_in_batch = self.save_checkpoint_decoder = self.save_checkpoint_embedding_generator = self.checkpoint_frequency = self.inverse_lookup = None
            self.FILE_for_training_results = open("saved_training_with_buffered_context_results.txt",'w')
            self.FILE_for_training_loss = open("training_loss_vs_iterations.txt",'w')

        def forward(self, sentence_tensor, mask):                                                   
            out_tensor = sentence_tensor
            for i in range(len(self.basic_decoder_arr)):                                                 
                out_tensor = self.basic_decoder_arr[i](out_tensor, mask)                              
            word_index = mask.shape[0]
            last_word_tensor = out_tensor[:,word_index]                                      
            last_word_onehot = self.out(last_word_tensor)        
            output_word_logprobs = nn.LogSoftmax(dim=1)(last_word_onehot)                                     
            _, idx_max = torch.max(output_word_logprobs, 1)                
            ## the logprobs are over the entire vocabulary of the tokenizer
            return output_word_logprobs, idx_max


        def sequence_predictor(self,input_tensor,gt_data,LOSS,mask,predicted_indexes):
            """
            This method is called by the training_step() method that follows.  The basic contract of this 
            method is to carry out a masked scan of the input sequence for predicting the next token at 
            each token position. Such predictions are autoregressive because each prediction depends 
            only on the previous tokens in the input sequence. 

            In the logic shown below, the predicted_indexes tensor contains the predicted integer index 
            for the token at each positional index in all the batch instances.
            
            On the other hand, the tensor predicted_word_index_values ONLY contains the predicted word 
            index value across the batch instances at ONE word position. Our goal is to fill the 
            predicted_indexes tensor one 'column' at a time through autoregressive predictions at each 
            token position.
            """
            for word_index in range(1,input_tensor.shape[1]):
                masked_input_seq = self.apply_mask(input_tensor, mask)                                
                predicted_word_logprobs, predicted_word_index_values = self(input_tensor, mask)
                loss = nn.NLLLoss()(predicted_word_logprobs, gt_data[:, word_index])           
                LOSS += loss
                mask = torch.cat((mask,torch.ones(1, device=input_tensor.device, dtype=torch.long)))  
                predicted_indexes[:,word_index] = predicted_word_index_values
            return LOSS,predicted_word_logprobs,predicted_word_index_values,predicted_indexes


        def training_step(self, batch, batch_idx):   
            """
            A network class that's meant to be trained with Lightnihg must provide an implementation
            for this method. In the first statement shown below, input_tensor is the output of the 
            embedding generator for a given sentence tensor.
            """
            input_tensor = torch.squeeze(batch[0])
            gt_data = torch.squeeze(batch[1])
            token_sequences_in_batch = batch[2]
            self.epoch_index = batch[3]
            master_decoder_optimizer = self.optimizers()
            master_decoder_scheduler = self.lr_schedulers()
            mask = torch.ones(1, device=input_tensor.device, dtype=torch.long)     ## initialize the mask
            predicted_indexes =torch.zeros(input_tensor.shape[:-1], device=input_tensor.device, dtype=torch.long)
            predicted_tokens = [[] for i in range(input_tensor.shape[0])]
            detokenized_predicted_word_sequence = [[] for i in range(input_tensor.shape[0])]
            predicted_word_logprobs = []
            LOSS = 0.0
            LOSS,predicted_word_logprobs,predicted_word_index_values,predicted_indexes = self.sequence_predictor(input_tensor,gt_data,LOSS,mask,predicted_indexes)
            self.log('train_loss', LOSS, on_step=True, on_epoch=True, prog_bar=True, logger=True)
            predicted_indexes = predicted_indexes.cpu().numpy()
            ## The replacement for the following accounts for the fact that the first token is the SOS token, followed by context-buffer tokens
            #  predicted_indexes = predicted_indexes[:, self.context_buffer_size:]              
            predicted_indexes = predicted_indexes[:, self.context_buffer_size+1:]              
            master_decoder_optimizer.zero_grad()
            self.manual_backward(LOSS)
            master_decoder_optimizer.step()                                                       
            master_decoder_scheduler.step()                                                       
            loss_normed = LOSS.item() / input_tensor.shape[0]
            self.loss_normed = loss_normed
            self.predicted_word_logprobs = predicted_word_logprobs
            self.running_loss += loss_normed
            self.prev_seq_logprobs =  predicted_word_logprobs
            if (batch_idx % 100 == 99) and (self.trainer.global_rank == 0):    
                self.avg_loss = self.running_loss / float(10)
                self.training_loss_tally.append(self.avg_loss)
                self.FILE_for_training_loss.write("%s\n" % str(self.avg_loss))
                self.running_loss = 0.0
                current_time = time.perf_counter()
                time_elapsed = current_time-self.start_time
                for param_group in master_decoder_optimizer.param_groups:
                    current_lr = param_group['lr']
                print("\n\n\n[epoch: %2d  iter:%4d  elapsed_time: %4d secs    lr: %.e]     loss: %.4f\n\n" % (self.epoch_index + 1, batch_idx+1,time_elapsed, current_lr, self.avg_loss)) 
                self.FILE_for_training_results.write("\n\n\n[epoch: %2d  iter:%4d  elapsed_time: %4d secs    lr: %.e]     loss: %.4f\n\n\n" % (self.epoch_index, batch_idx+1,time_elapsed, current_lr, self.avg_loss)) 

                for j in range(self.batch_size):
                    predicted_tokens[j] = self.tokenizer.decode( predicted_indexes[j], skip_special_tokens=True )
                for i in random.sample( range(self.batch_size), 4 ): 
                    print("Ground-Truth: ", self.detokenizer( ' '.join(token_sequences_in_batch[i]) ))
                    print("GT Token Seq: ", ' '.join(token_sequences_in_batch[i] ))
                    print("   Predicted: ", predicted_tokens[i])
                    print(" Detokenized: ", self.detokenizer( self.tokenizer.decode( predicted_indexes[i], skip_special_tokens=True ) ))
                    print()
                    self.FILE_for_training_results.write("Ground-truth: %s\n" % str(self.detokenizer( ' '.join(token_sequences_in_batch[i]) )))
                    self.FILE_for_training_results.write("GT Token Seq: %s\n" % str(' '.join(token_sequences_in_batch[i]) ))
                    self.FILE_for_training_results.write("   Predicted: %s\n" % str(predicted_tokens[i]))
                    self.FILE_for_training_results.write(" Detokenized: %s\n" % str(self.detokenizer( self.tokenizer.decode(predicted_indexes[i],skip_special_tokens=True))))
                    self.FILE_for_training_results.write("\n")
                self.accum_times.append(current_time-self.start_time)
                self.FILE_for_training_results.flush()
                self.FILE_for_training_loss.flush()
            if ((batch_idx % self.checkpoint_frequency) == (self.checkpoint_frequency-1)) and  (self.trainer.global_rank == 0)  :    
                print("\n\nSaving checkpoint at iteration: %d\n\n"% (batch_idx+1))
                self.save_checkpoint_decoder(self, self.checkpoint_dir, batch_idx+1)
                global embedding_generator
                self.save_checkpoint_embedding_generator(embedding_generator, self.checkpoint_dir, self.training_iter+1)
            self.training_iter += 1

        def configure_optimizers(self):
            """
            For the learning rates, I have used a combination of a Linear warmup scheduler followed by a Cosine scheduler with restarts.
            For the LinearLR scheduler, the lr specified for the optimizer is multiplied by the two factors shown for the variations 
            over the duration of the warmup in terms of the number of learning iterations involved.
            For the Cosine-with-restarts scheduler, T_0 is number of iterations in one period of the cosine. After the first cosine,
            these periods become longer (or shorter) as they are multiplied by T_mult.  The maximum learning rate during cosine
            scheduling is the value of lr given to the optimizer and the minimum learning rate is specified by eta_min.
            """
            optimizer=torch.optim.AdamW(params=self.parameters(),lr=1e-4 )
            warmup_scheduler = LinearLR(optimizer, start_factor=1e-4, end_factor=1.0, total_iters=self.n_warmup_steps, last_epoch=-1)
            #  cosine_scheduler = CosineAnnealingLR(optimizer,T_max=5,  eta_min=1e-6, last_epoch=-1)
            cosine_scheduler = CosineAnnealingWarmRestarts(optimizer, T_0=500, T_mult=2, eta_min=1e-5, last_epoch=-1)
            combined = SequentialLR(optimizer, schedulers=[warmup_scheduler, cosine_scheduler], milestones=[self.n_warmup_steps])
            return {'optimizer': optimizer,'lr_scheduler':combined}

        def apply_mask(self, sentence_tensor, mask):  
            out = torch.zeros_like(sentence_tensor)
            out[:,:len(mask),:] = sentence_tensor[:,:len(mask),:] 
            return out    

    ###%%%
    #######################################################################################################################
    ############################################### Training babyGPT  #####################################################

    def save_decoder(self, decoder):
        "Save the trained decoder to a disk file"       
        torch.save(decoder.state_dict(), self.gpt.path_saved_model["saved_decoder"])

    def save_embedding_generator(self, embedding_generator):
        torch.save(embedding_generator.state_dict(), self.gpt.path_saved_model["saved_embeddings_generator"])

    def save_checkpoint_decoder(self, decoder, dir_name, iter_index):
        "Save the decoder checkpoint"       
        torch.save(decoder.state_dict(), dir_name + "/saved_decoder_" + str(iter_index))

    def save_checkpoint_embedding_generator(self, embedding_generator, dir_name, iter_index):
        "save checkpoint for the embedding_generator"
        torch.save(embedding_generator.state_dict(), dir_name + "/saved_embedding_generator_" + str(iter_index))        


    def run_code_with_buffered_context_for_training_TransformerFG(self, xformer, master_decoder, dataloader, 
                                                           checkpoint_frequency=4000, display_train_loss=False ):
        """
        Drawn from the training routines in the Transformer module of DLStudio
        """
        global embedding_generator

        def detokenizer( token_sequence_as_string ):
            regex = r'\s_\s'
            out_words = ""
            try:
                out_words = re.split(regex, token_sequence_as_string)
            except TypeError as e:
                print(e)
                return [""] * len(token_sequence_as_string)
            ## Join together the space-separated token fragments into complete words, but make sure 
            ## you do NOT cross punctuation marks:
            new_all_words = []
            for word in out_words:
                 frag = word
                 while re.search( r'\w+\s\w+', frag ):
                     frag =  re.sub(r'(\w+)\s(\w+)', r'\1\2', frag)
                 new_all_words.append(frag)
            ## If a word obtained from the previous step include a fragment that terminates in a 
            ## punctuation mark which can be any of ".?,!]+.?", break it into two or more subwords:
            cleaned_all_words = []
            for word in new_all_words:
                new_words = []   
                if any(char in string.punctuation for char in word):
                    parts = re.findall(r'[^.?,!]+.?', word)
                    cleaned_all_words += parts
                else:
                    cleaned_all_words.append(word)
            return ' '.join(cleaned_all_words)

        checkpoint_dir =  "checkpoint_dir"

        if os.path.exists(checkpoint_dir):  
            files = glob.glob(checkpoint_dir + "/*")
            for file in files: 
                if os.path.isfile(file): 
                    os.remove(file) 
                else: 
                    files = glob.glob(file + "/*") 
                    list(map(lambda x: os.remove(x), files)) 
        else: 
            os.mkdir(checkpoint_dir)   


        class LocalLoader(IterableDataset):
            def __init__(self, data_source, batchsize, context_window_size, context_buffer_size, inv_lookup_fn):
                super(LocalLoader).__init__()
                self.data_source = data_source              
                self.batchsize = batchsize
                self.context_window_size = context_window_size
                self.context_buffer_size = context_buffer_size
                self.inv_lookup_fn = inv_lookup_fn
                self.prev_iteration_data = np.zeros((batchsize, context_buffer_size), dtype=int)
                self.datasource_access_index = 0
                self.epoch_index = 0

            def __iter__(self):
                """
                Lightning requires the dataloader to be a Generator
                """
                while True:                    
                    try:
                        new_data = self.data_source[self.datasource_access_index]
                    except StopIteration:
                        self.datasource_access_index = 0
                        self.epoch_index += 1                          
                        new_data = self.data_source[self.datasource_access_index]         
                    self.datasource_access_index += 1
#                    epoch_index = self.data_source.epoch_index 
                    new_prev = new_data[:, -self.context_buffer_size:]
                    token_sequences = [ [self.inv_lookup_fn[c] for c in new_data[i][1:]] for i in range(self.batchsize) ]
                    first_tokens = new_data[:, 0, None]
                    data = np.concatenate( (first_tokens, self.prev_iteration_data, new_data[:, 1:]), axis=1 )
                    tensor_data = torch.from_numpy(data)
                    global embedding_generator
                    input_tensor = embedding_generator(tensor_data).detach() 
                    self.prev_iteration_data = new_prev
                    yield (input_tensor, tensor_data, token_sequences, self.epoch_index)


        class StreamingDataModule(L.LightningDataModule):
            """
            In the parameter list for the constructor __init__, you see two items that appear to be similar:

                                          batchsize   and    batch_size 

            Note that these have difference meanings.  The first, batchsize, is set to the batch size as set in the
            ArticleGenerator module.  This is likely to be a number like 50 in my experiments with babyGPT.  The second,
            batch_size, is related to any batching carried out by Lightning's LinghtningDataModule.  Since we do not
            want additional batching to be carried out by LinghtningDataModule, I have set batch_size to None.

            Also note the parameter num_workers shown below.  If you are using N GPUs, Lightning would want to create
            4*N threads.  You need to make sure that this number is less the maximum number of threads that your OS
            can support.
            """
#            def __init__(self, data_source, context_window_size, batchsize, context_buffer_size, inv_lookup_fn, batch_size=None, num_workers=4):
            def __init__(self, data_source, context_window_size, batchsize, context_buffer_size, inv_lookup_fn, batch_size=None, num_workers=0):
                super(StreamingDataModule, self).__init__()
                self.context_window_size = context_window_size
                self.context_buffer_size = context_buffer_size
                self.inv_lookup_fn = inv_lookup_fn
                self.data_source = data_source
                self.batchsize = batchsize
                self.num_workers = num_workers

            def setup(self, stage=None):
                self.train_dataset = LocalLoader(self.data_source, self.batchsize, self.context_window_size, self.context_buffer_size, self.inv_lookup_fn)
            def train_dataloader(self):
                return DataLoader(self.train_dataset, batch_size=None, num_workers=self.num_workers) 

        global embedding_generator
        embedding_generator = self.EmbeddingGenerator(xformer, self.embedding_size)

        ## torch.set_float32_matmul_precision('medium')         
        torch.set_float32_matmul_precision('high')

        master_decoder.save_checkpoint_decoder = self.save_checkpoint_decoder
        master_decoder.save_checkpoint_embedding_generator = self.save_checkpoint_embedding_generator
        master_decoder.checkpoint_frequency =  checkpoint_frequency
        master_decoder.checkpoint_dir =  checkpoint_dir
        master_decoder.epoch_index = dataloader.epoch_index            ## this just provides the value for epoch_index at the start of training.
        master_decoder.tokenizer = dataloader.tokenizer
        master_decoder.detokenizer = detokenizer
        master_decoder.inverse_lookup = dataloader.inverse_lookup

        logger = TensorBoardLogger("lightning_logs", name="babyGPT")    ## This creates a directory named 'lightning_logs' and under that
                                                                        ## a sub-directory named 'babyGPT' for the recording the losses.
        trainer =  L.Trainer(devices=-1, 
                             accelerator="gpu", 
                             strategy='ddp_find_unused_parameters_true', 
                             enable_progress_bar=False,      ## to disable the progress bar at the bottom of the screen
                             logger=logger,
                             max_epochs=-1,
                             log_every_n_steps=100
                            )

        trainer.fit( model=master_decoder,  
                     train_dataloaders= StreamingDataModule(data_source=dataloader,
                                                            context_window_size=dataloader.context_window_size,
                                                            batchsize=dataloader.batch_size,
                                                            context_buffer_size=dataloader.context_buffer_size,
                                                            inv_lookup_fn=dataloader.inverse_lookup))
    ###%%%
    #######################################################################################################################
    ###########################################  PromptResponder for babyGPT  #############################################

    class PromptResponder(nn.Module):
        """
        Prompting a trained babyGPT models means that you supply a small number of words (as, say, the 
        beginning of a new thought) as a prompt and the model supplies the rest of the words to complete 
        the thought.  The class comes with two methods, the first for extending your prompt until it 
        reaches a period, and the second for going beyond the first period encountered.
    
        Any interaction with a trained GPT model has to deal with the following issue:  What to do with
        the context buffer that is meant to be a continuation of the last part of the previous "sentence"
        fed into the transformer. 
    
        Ideally, we should be placing in the context buffer words that create a context for the prompt.
        But there is no easy way to that without a more elaborate model. An example of more elaborate
        modeling would be to have the input to the transformer consist of, say, an SOS token, a special
        context token consisting possibly of integer index values beyond the tokenizer vocab, followed
        by a context buffer that would be the last part of the previous sentence, followed, finally, 
        by the new input tokens.
    
        babyGPT gives you two options regarding what to do with the context buffer for your prompt:
    
                --  all_zeros
    
                --  get_from_prompt
    
        With the first option, all of the integer encoding values in the context buffer are set to
        the integer zero.  And, with the second option, at this time, the context buffer contains
        a portion or all of the prompt itself.  If the tokenized version of the prompt is shorter
        than the size of the context buffer, only the context_buffer_size number of elements of the
        prompt are retained for the context buffer.  In the opposite case, just the initial 
        context_buffer_size number of elements of the prompt are retained.
        """
        def __init__(self, gpt,  xformer, master_decoder, context_window_size, context_buffer_size, tokenizer_json, checkpoint_dir, checkpoint_index):
            super(babyGPT.PromptResponder, self).__init__()
            self.gpt  =  gpt
            self.xformer = xformer
            self.master_decoder = master_decoder
            self.context_window_size = context_window_size
            self.context_buffer_size = context_buffer_size
            self.tokenizer_json = tokenizer_json                       
            self.tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.tokenizer_json)
            FILE = open(self.tokenizer_json)    
            tokenizer_dict =  json.load( FILE ) 
            self.inverse_lookup  =  {v:k for k,v in tokenizer_dict['model']['vocab'].items()}  
            self.vocab_size = self.tokenizer.vocab_size
            self.checkpoint_dir = checkpoint_dir
            self.checkpoint_index = checkpoint_index


        def generate_response_to_prompt_up_to_period(self, context_buffer_option=None, result_file=None):
            """
            This version tries to construct a more elaborate response to a single prompt by going beyond the first period that 
            is encountered.  The first part of the if-else block shown below is for extending the prompt to the first period.
            On the other hand, the else clause is for generating additional sentences beyond the first period.  I have yet to
            clean up the logic for that.
            """

            def detokenizer( token_sequence_as_string ):
                regex = r'\s_\s'
                out_words = ""
                try:
                    out_words = re.split(regex, token_sequence_as_string)
                except TypeError as e:
                    print(e)
                    return [""] * len(token_sequence_as_string)
                ## Join together the space-separated token fragments into complete words, but make sure 
                ## you do NOT cross punctuation marks:
                new_all_words = []
                for word in out_words:
                     frag = word
                     while re.search( r'\w+\s\w+', frag ):
                         frag =  re.sub(r'(\w+)\s(\w+)', r'\1\2', frag)
                     new_all_words.append(frag)
                ## If a word obtained from the previous step include a fragment that terminates in a 
                ## punctuation mark which can be any of ".?,!]+.?", break it into two or more subwords:
                cleaned_all_words = []
                for word in new_all_words:
                    new_words = []   
                    if any(char in string.punctuation for char in word):
                        parts = re.findall(r'[^.?,!]+.?', word)
                        cleaned_all_words += parts
                    else:
                        cleaned_all_words.append(word)
                return ' '.join(cleaned_all_words)

            def dev():                                                                                                              
                if torch.cuda.is_available():                                                                                       
                    return torch.device(f"cuda:0")                                                                                  
                return torch.device("cpu")

            if result_file is not None:
                FILE = open(result_file, 'w')

            master_decoder = self.master_decoder
            master_decoder.load_state_dict(torch.load(self.checkpoint_dir + "/" + 
                                                        self.gpt.path_saved_model['decoder'] +  '_' + str(self.checkpoint_index) ))
            master_decoder.to( dev() )     
            embedding_generator = self.gpt.EmbeddingGenerator(self.xformer, self.gpt.embedding_size).to( dev() )
            embedding_generator.load_state_dict(torch.load(self.checkpoint_dir + "/" +
                                                   self.gpt.path_saved_model['embedding_generator'] + '_' + str(self.checkpoint_index)))
            embedding_generator.to( dev() )
            debug = False
            prompt = ""
            with torch.no_grad():
                while True:
                    context_buffer = np.zeros(shape=(self.context_buffer_size), dtype=int)
                    while True:
                        prompt = input("\nEnter your prompt: ")
                        if prompt == "": continue
                        else: break
                    ##  Strip any empty space before or after the prompt:
                    prompt = prompt.strip()
                    print("\nyour prompt: ", prompt)
                    all_words = prompt.split()
                    all_words = [word + " _" if re.search(r'.*[\w]$', word) else word for word in all_words]
                    prompt_text = ' '.join(all_words)
                    print("\nprompt_text_with_underscores: ", prompt_text)
                    ## consists of int tokens for the symbolic token in prompt:
                    encoded_prompt = self.tokenizer.encode( prompt_text )
                    token_sequence_in_prompt = [self.inverse_lookup[int_code] for int_code in encoded_prompt]
                    print("\ntoken_sequence_in_prompt: ", token_sequence_in_prompt)
                    print("\nencoded_prompt: ", encoded_prompt)
                    predicted_word_index_value = torch.zeros(1, dtype=torch.int)
                    stopping_token_code = 46
                    while predicted_word_index_value.item() != stopping_token_code:
                        if len(encoded_prompt) >=  self.context_window_size: 
                            break
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,0] = 89         ##  The SOS token             
                        if context_buffer_option == "all_zeros":
#                            print("\n\n======================== Choosing all-zeros option for context initialization")
                            input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        elif context_buffer_option == "get_from_prompt": 
#                            print("\n\n======================== Choosing 'get from prompt' option for context initialization")
                            if len(encoded_prompt) > self.context_buffer_size:
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(encoded_prompt[:self.context_buffer_size])
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)    
                            else:
                                ## if prompt is too short:
                                padded_encoded_prompt =  encoded_prompt +  [0] * (self.context_buffer_size - len(encoded_prompt))
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(padded_encoded_prompt)
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        input_tensor = input_tensor.to( dev() )
                        input_tensor = embedding_generator( input_tensor )
                        mask = torch.ones( self.context_buffer_size + len(encoded_prompt), dtype=int)
                        predicted_word_index_value = torch.zeros(1, dtype=torch.int)
                        predicted_word_logprobs, predicted_word_index_value = master_decoder(input_tensor, mask)                     
                        predicted_token =  self.xformer.inverse_lookup[predicted_word_index_value.cpu().numpy()[0]]
                        encoded_prompt.append(predicted_word_index_value.item())
                        if debug: 
                            print("\npredicted token: ", predicted_token)                
                            print("\nencoded_prompt: ", encoded_prompt)                
                    if debug:
                        print("\n\nprompt and its response: ", encoded_prompt)
                    output_string = ""
                    for code in encoded_prompt:
                        output_string += " " + self.xformer.inverse_lookup[code]
                    print("\nencoding of prompt and the response: ", encoded_prompt)
                    print("\nprompt and its response: ", output_string)
                    final_output = detokenizer(output_string) 
                    ## find() returns -1 when no char is "."
                    index_period  =  final_output.find(".")
                    if index_period >= 0 and index_period < len(final_output):
                        print("\ndetokenized sentence completion: ", final_output[:final_output.find(".")+1])
                    else:
                        print("\ndetokenized sentence completion: ", final_output)


        def generate_response_to_prompt_beyond_period(self, context_buffer_option=None, result_file=None):
            """
            This version tries to construct a more elaborate response to a single prompt by going beyond the first period that 
            is encountered.  The first part of the if-else block shown below is for extending the prompt to the first period.
            On the other hand, the else clause is for generating additional sentences beyond the first period.  I have yet to
            clean up the logic for that.xs
            """
            def detokenizer( token_sequence_as_string ):
                regex = r'\s_\s'
                out_words = ""
                try:
                    out_words = re.split(regex, token_sequence_as_string)
                except TypeError as e:
                    print(e)
                    return [""] * len(token_sequence_as_string)
                ## Join together the space-separated token fragments into complete words, but make sure 
                ## you do NOT cross punctuation marks:
                new_all_words = []
                for word in out_words:
                     frag = word
                     while re.search( r'\w+\s\w+', frag ):
                         frag =  re.sub(r'(\w+)\s(\w+)', r'\1\2', frag)
                     new_all_words.append(frag)
                ## If a word obtained from the previous step include a fragment that terminates in a 
                ## punctuation mark which can be any of ".?,!]+.?", break it into two or more subwords:
                cleaned_all_words = []
                for word in new_all_words:
                    new_words = []   
                    if any(char in string.punctuation for char in word):
                        parts = re.findall(r'[^.?,!]+.?', word)
                        cleaned_all_words += parts
                    else:
                        cleaned_all_words.append(word)
                return ' '.join(cleaned_all_words)

            if result_file is not None:
                FILE = open(result_file, 'w')
            master_decoder = self.master_decoder
            master_decoder.load_state_dict(torch.load(self.checkpoint_dir + "/" + 
                                                        self.gpt.path_saved_model['decoder'] +  '_' + str(self.checkpoint_index) ))
            master_decoder.to( dev() )     
            embedding_generator = self.gpt.EmbeddingGenerator(self.xformer, self.gpt.embedding_size).to( dev() )
            embedding_generator.load_state_dict(torch.load(self.checkpoint_dir + "/" +
                                                   self.gpt.path_saved_model['embedding_generator'] + '_' + str(self.checkpoint_index)))
            embedding_generator.to( dev() )
            debug = False
            with torch.no_grad():
                interaction_index = 0
                overall_response = ""
                while True:
                    if interaction_index == 0:                                                                              ## (A)

                        context_buffer = np.zeros(shape=(self.context_buffer_size), dtype=int)
                        prompt = input("\n\nEnter your prompt: ")
                        ##  Strip any empty space before or after the prompt:
                        prompt = prompt.strip()
                        print("\n\nyour prompt: ", prompt)
                        all_words = prompt.split()
                        all_words = [word + " _" if re.search(r'.*[\w]$', word) else word for word in all_words]
                        prompt_text = ' '.join(all_words)
                        print("\n\nprompt_text_with_underscores: ", prompt_text)
                        ## consists of int tokens for the symbolic token in prompt:
                        encoded_prompt = self.tokenizer.encode( prompt_text )
                        token_sequence_in_prompt = [self.inverse_lookup[int_code] for int_code in encoded_prompt]
                        print("\n\ntoken_sequence_in_prompt: ", token_sequence_in_prompt)
                        print("\n\nencoded_prompt: ", encoded_prompt)
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,0] = 89         ##  The SOS token             
                        if context_buffer_option == "all_zeros":
                            input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        elif context_buffer_option == "get_from_prompt": 
                            if len(encoded_prompt) > self.context_buffer_size:
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(encoded_prompt[:self.context_buffer_size])
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)    
                            else:
                                ## if prompt is too short:
                                padded_encoded_prompt =  encoded_prompt +  [0] * (self.context_buffer_size - len(encoded_prompt))
                                input_tensor[0,1:1+self.context_buffer_size] = torch.tensor(padded_encoded_prompt)
                                input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)

                    else:                                                                                                   ## (B)
                        print("\n\n\n[Interaction no. %d]  encoded prompt from PREV ITER: " % (interaction_index+1), encoded_prompt) 
                        context_buffer =  encoded_prompt[-self.context_buffer_size - self.context_buffer_size:-self.context_buffer_size]
                        encoded_prompt = encoded_prompt[-self.context_buffer_size:]
                        print("[Interaction no. %d]  context_buffer: " % (interaction_index+1), context_buffer)
                        print("[Interaction no. %d]  encoded prompt: " % (interaction_index+1), encoded_prompt) 
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,:self.context_buffer_size] = torch.tensor( context_buffer )
                        input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                    interaction_index += 1               
                    if interaction_index >= 3: 
                        print("\n\nInteraction limit reached")
                        break
                    input_tensor = input_tensor.to( dev() )
                    input_tensor = embedding_generator( input_tensor )
                    mask = torch.ones( self.context_buffer_size + len(encoded_prompt), dtype=int)
                    stopping_token_code = 16
                    predicted_word_index_value = torch.zeros(1, dtype=torch.int)
                    while predicted_word_index_value.item() != stopping_token_code:
                        if len(encoded_prompt) >=  self.context_window_size: 
                            break
                        predicted_word_logprobs, predicted_word_index_value = master_decoder(input_tensor, mask)                 
                        predicted_token =  self.xformer.inverse_lookup[predicted_word_index_value.cpu().numpy()[0]]
                        encoded_prompt.append(predicted_word_index_value.item())
                        if debug: 
                            print("\npredicted token: ", predicted_token)                
                            print("\nencoded_prompt: ", encoded_prompt)                
                        input_tensor = torch.zeros( 1, self.xformer.max_seq_length, dtype=torch.int )
                        input_tensor[0,self.context_buffer_size:self.context_buffer_size + len(encoded_prompt)] = torch.tensor(encoded_prompt)
                        input_tensor = input_tensor.to( dev() )
                        input_tensor = embedding_generator( input_tensor )
                        mask = torch.cat( ( mask, torch.ones(1, dtype=int) ) )                                          
                    if debug:
                        print("\n\nprompt and its response: ", encoded_prompt)
                    output_string = ""
                    for code in encoded_prompt:
                        output_string += " " + self.xformer.inverse_lookup[code]
                    print("\n\nprompt and its response: ", output_string)
                    print("\n\ndetokenized sentence completion: ", detokenizer(output_string))

                    overall_response += output_string

            print("\n\nOverall response to your prompt: ", overall_response)
            print("\n\nOverall detokenized response: ", detokenizer(overall_response))


#############################################################################################################################
##############################################   End of babyGPT Class Definition#############################################

if __name__ == '__main__': 
    pass

