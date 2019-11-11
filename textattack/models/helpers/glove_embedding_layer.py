import torch

import numpy as np
import torch.nn as nn

import textattack.utils as utils

logger = utils.get_logger()

class EmbeddingLayer(nn.Module):
    """
        A layer of a model that replaces word IDs with their embeddings. 
        
        This is a useful abstraction for any nn.module which wants to take word IDs
        (a sequence of text) as input layer but actually manipulate words'
        embeddings.
        
        Requires some pre-trained embedding with associated word IDs.
    """
    def __init__(self, n_d=100, embs=None, fix_emb=True, oov='<oov>', pad='<pad>', normalize=True):
        super(EmbeddingLayer, self).__init__()
        word2id = {}
        if embs is not None:
            embwords, embvecs = embs
            for word in embwords:
                assert word not in word2id, "Duplicate words in pre-trained embeddings"
                word2id[word] = len(word2id)

            logger.debug(f'{len(word2id)} pre-trained word embeddings loaded.\n')
            
            n_d = len(embvecs[0])

        if oov not in word2id:
            word2id[oov] = len(word2id)

        if pad not in word2id:
            word2id[pad] = len(word2id)

        self.word2id = word2id
        self.n_V, self.n_d = len(word2id), n_d
        self.oovid = word2id[oov]
        self.padid = word2id[pad]
        self.embedding = nn.Embedding(self.n_V, n_d)
        self.embedding.weight.data.uniform_(-0.25, 0.25)

        if embs is not None:
            weight  = self.embedding.weight
            weight.data[:len(embwords)].copy_(torch.from_numpy(embvecs))
            print(f"EmbeddingLayer shape: {weight.size()}")

        if normalize:
            weight = self.embedding.weight
            norms = weight.data.norm(2,1)
            if norms.dim() == 1:
                norms = norms.unsqueeze(1)
            weight.data.div_(norms.expand_as(weight.data))

        if fix_emb:
            self.embedding.weight.requires_grad = False

    def forward(self, input):
        return self.embedding(input)

class GloveEmbeddingLayer(EmbeddingLayer):
    """ Pre-trained Global Vectors for Word Representation (GLOVE) vectors.
        Uses embeddings of dimension 200.
        
        GloVe is an unsupervised learning algorithm for obtaining vector 
        representations for words. Training is performed on aggregated global 
        word-word co-occurrence statistics from a corpus, and the resulting 
        representations showcase interesting linear substructures of the word 
        vector space.
        
        
        GloVe: Global Vectors for Word Representation. (Jeffrey Pennington, 
            Richard Socher, and Christopher D. Manning. 2014.)
    """
    EMBEDDING_PATH = '/net/bigtemp/jg6yd/treeattack/glove/glove.6B.200d.txt'
    def __init__(self):
        utils.download_if_needed(GloveEmbeddingLayer.EMBEDDING_PATH)
        super().__init__(embs=load_embedding(GloveEmbeddingLayer.EMBEDDING_PATH))

def load_embedding_npz(path):
    """ Loads a word embedding from a numpy binary file. """
    data = np.load(path)
    return [ w.decode('utf8') for w in data['words'] ], data['vals']

def load_embedding_txt(path):
    """ Loads a word embedding from a text file. """
    file_open = gzip.open if path.endswith(".gz") else open
    words = [ ]
    vals = [ ]
    with file_open(path, encoding='utf-8') as fin:
        fin.readline()
        for line in fin:
            line = line.rstrip()
            if line:
                parts = line.split(' ')
                words.append(parts[0])
                vals += [float(x) for x in parts[1:]]
    return words, np.asarray(vals).reshape(len(words),-1)

def load_embedding(path):
    """ Loads a word embedding from a numpy binary file or text file. """
    if path.endswith(".npz"):
        return load_embedding_npz(path)
    else:
        return load_embedding_txt(path)