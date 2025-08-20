import babyGPT
import os
import unittest


from babyGPT import *

class TestDecoderInstall(unittest.TestCase):

    def setUp(self):
        urls = ['https://xyz.com']
        articles_dir = 'saved_articles_dir'
        tokenizer_json  =  '../Examples/109_babygpt_tokenizer_49275.json'
        max_seq_length = 10
        context_window_size = 25
        context_buffer_size = 5
        batch_size = 4
        embedding_size = 128
        num_basic_decoders = num_atten_heads = 4     
        optimizer_params = {'beta1' : 0.9,  'beta2': 0.98,  'epsilon' : 1e-6}
        num_warmup_steps = 4000
        masking = True       
        baby_gpt = babyGPT(
                            urls  =  urls,
                            max_seq_length = max_seq_length,
                            batch_size = batch_size,
                            embedding_size = embedding_size,
                            num_basic_decoders = num_basic_decoders,
                            num_atten_heads = num_atten_heads,
                            optimizer_params = {'beta1' : 0.9,  'beta2': 0.98,  'epsilon' : 1e-6},
                            num_warmup_steps = num_warmup_steps,
                            masking = masking,
                            use_gpu = True,
                            verify_text_corpus = True,
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
        
        self.number_of_learnable_params_in_decoder = sum(p.numel() for p in master_decoder.parameters() if p.requires_grad)
##        print("\n\nThe number of learnable parameters in the Master Decoder: %d" % self.number_of_learnable_params_in_decoder)
        
    def test_decoder_install(self):
        available = False
        print("testing master decoder installation")
        if self.number_of_learnable_params_in_decoder  >  7000000:
            available = True
        self.assertEqual(available, True)

def getTestSuites(type):
    return unittest.TestSuite([
            unittest.makeSuite(TestDecoderInstall, type)
                             ])                    
if __name__ == '__main__':
    unittest.main()

