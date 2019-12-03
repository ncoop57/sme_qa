
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# file to edit: dev_nb/evaluation.ipynb

# imports
from fastai.text import *

# Evaluation metrics for vulnerability detection - Accuracy, Precision, Recall
def eval_vuln(mdl, tst, sp, task, max_toks):
    tps, tns, fps, fns = 0, 0, 0, 0
    tot = 0
    for inpt, lbl in zip(tst["query"], tst["res"]):
        pred = get_clas_res(mdl, "xxbos " + inpt, sp, task, n_toks = max_toks)
        if lbl == "yes":
            if pred == lbl:
                tps += 1
            else: fns += 1
        else:
            if pred == lbl:
                tns += 1
            else: fps += 1

        tot += 1
        torch.cuda.empty_cache()

    acc   = (tps + tns) / tot
    prec  = tps / (tps + fps) if (tps + fps) != 0 else 0.
    recal = tps / (tps + fns) if (tps + fns) != 0 else 0.

    return acc, prec, recal

# Dependency downloads
import nltk
# required for meteor to perform similarity score, etc by looking for synonyms, antonyms...
nltk.download('wordnet')

from typing import List
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')

def _eval_bleu(reference_texts: List[str], generated_text: str, weights: List[int]):
    tokenized_references = [tokenizer.tokenize(reference) for reference in reference_texts]
    tokenized_generated_text = tokenizer.tokenize(generated_text)
    return round(sentence_bleu(
        tokenized_references,
        tokenized_generated_text,
        weights=weights),
        4)

def eval_bleu1(reference_texts: List[str], generated_text: str):
    return _eval_bleu(reference_texts,
                      generated_text,
                      weights = (1,0,0,0))

def eval_bleu2(reference_texts: List[str], generated_text: str):
    return _eval_bleu(reference_texts,
                      generated_text,
                      weights = (0.5,0.5,0,0))

def eval_bleu3(reference_texts: List[str], generated_text: str):
    return _eval_bleu(reference_texts,
                      generated_text,
                      weights = (0.33,0.33,0.33,0))

def eval_bleu4(reference_texts: List[str], generated_text: str):
    return _eval_bleu(reference_texts,
                      generated_text,
                      weights = (0.25,0.25,0.25,0.25))

from nltk.translate.meteor_score import meteor_score
def eval_meteor(reference_texts: List[str], generated_text: str):
    return round(meteor_score(reference_texts, generated_text, preprocess=str.lower), 4)

nltk.download('punkt')

import rouge
import pandas as pd

def _eval_rougeL_single_ref(reference_text: str, generated_text: str):
    evaluator = rouge.Rouge(metrics=['rouge-l'],
                           max_n=4,
#                            limit_length=True,
#                            length_limit=100,
#                            length_limit_type='words',
                           apply_avg=0,
                           apply_best=0,
                           alpha=0.5, # Default F1_score
                           weight_factor=1.2,
                           stemming=True)
    # scores = evaluator.get_scores(all_hypothesis, all_references)
    # watch out, it takes hypothesis first and then references.
    score = evaluator.get_scores(generated_text, reference_text)['rouge-l'][0]
    score_p = score['p'][0]
    score_f = score['f'][0]
    score_r = score['r'][0]
    return [score_p, score_r, score_f]

def eval_rougeL_single_ref(reference_text: List[str], generated_text: str):
    evaluator = rouge.Rouge(metrics=['rouge-l'],
                           max_n=4,
#                            limit_length=True,
#                            length_limit=100,
#                            length_limit_type='words',
                           apply_avg=0,
                           apply_best=0,
                           alpha=0.5, # Default F1_score
                           weight_factor=1.2,
                           stemming=True)
    # scores = evaluator.get_scores(all_hypothesis, all_references)
    # watch out, it takes hypothesis first and then references.
    score = evaluator.get_scores(generated_text, reference_text[0])['rouge-l'][0]
    score_p = score['p'][0]
    score_f = score['f'][0]
    score_r = score['r'][0]
    return (score_p, score_r, score_f)

def eval_rougeL(reference_texts: List[str], generated_text: str):
    scores = [
        _eval_rougeL_single_ref(
            reference,
            generated_text)
        for reference in reference_texts]
#     return scores
    result_df = pd.DataFrame(scores)
    # be extra careful, mislabeling is going to be really damaging.
    result_df.columns=['p', 'r', 'f']
    return result_df


def eval_txt(mdl, ds, sp, task, max_toks):
    b1, b2, b3, b4 = [], [], [], []
    meteor = []
    rouge_l = []
    levenshtein = []
    cosine = []
    jaccard = []
    preds = []
    tokenizer = Tokenizer()
    for inpt, lbl in zip(ds["query"], ds["res"]):
        pred = get_seq_res(mdl, "xxbos " + inpt, sp, task, n_toks = max_toks)

        lbl = ' '.join(lbl.split())
        preds.append((pred, lbl))

        # bleu 1-4
        b1.append(eval_bleu1([lbl], pred))
        b2.append(eval_bleu2([lbl], pred))
        b3.append(eval_bleu3([lbl], pred))
        b4.append(eval_bleu4([lbl], pred))

        # meteor
        meteor.append(eval_meteor([lbl], pred))

        # Levenshtein
        levenshtein.append(levenshtein_distance_score(lbl, pred))

        # Similarities
        cosine.append(get_cosine_sim(lbl, pred))
        jaccard.append(get_jaccard_sim(lbl, pred))

        # rouge
        rouge_l.append(eval_rougeL_single_ref([lbl], pred))

    return b1, b2, b3, b4, meteor, rouge_l, levenshtein, cosine, jaccard, preds

# Grabs entire model's response up until special xxbos token,
# i.e. once model begins a new sentence we consider the model finished with its answer.
def get_res(mdl, inpt, sp, task, n_toks = 1_000, greedy = False):
    if greedy:
        res = mdl.beam_search(inpt, n_words = n_toks, beam_sz = 1, top_k = 1).split(" ")
        res = sp.DecodePieces(res).split(" ")[1:]
    else:
        res = mdl.predict(inpt, n_toks, temperature=0.75).split(" ")
        res = sp.DecodePieces(res).split(" ")

    try:
        end_res = res.index("xxbos")
    except:
        end_res = len(res) - 1

    res = " ".join(res[:end_res])
    res = res[res.find(task) + len(task):]

    return res

# Grabs entire model's response up until special xxbos token for a sequence task,
# i.e. once model begins a new sentence we consider the model finished with its answer.
def get_seq_res(mdl, inpt, sp, task, n_toks = 1_000):
    res = mdl.predict(inpt, n_toks, temperature=0.75).split(" ")
    res = sp.DecodePieces(res).replace(task, " ").split(" ")[1:]

    try:
        end_res = res.index("xxbos")
    except:
        end_res = len(res) - 1

    res = decode_spec_tokens(res[:end_res])
    res = " ".join(res[:end_res])

    return res

# Grabs entire model's response up until special xxbos token for a classification task,
# i.e. once model begins a new sentence we consider the model finished with its answer.
def get_clas_res(mdl, inpt, sp, task, n_toks = 10):
    res = mdl.beam_search(inpt, n_words = n_toks, beam_sz = 1, top_k = 1).split(" ")
    res = sp.DecodePieces(res).split(" ")[2:]

    try:
        end_res = res.index("xxbos")
    except:
        end_res = len(res) - 1

    res = " ".join(res[:end_res])
    res = res[res.find(task) + len(task):]

    return res

# priya

from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _get_vectors(*strs):
    text = [t for t in strs]
    vectorizer = CountVectorizer(text)
    vectorizer.fit(text)
    return vectorizer.transform(text).toarray()

def get_cosine_sim(reference_txt:str, generated_txt:str):
    vectors = [t for t in _get_vectors(reference_txt, generated_txt)]
    return round(cosine_similarity(vectors[0:1], vectors)[0][1],4)

# priya

from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import wordnet
lmtzr = WordNetLemmatizer()

def _get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def _lemmatizeSentence(strr):
    return ([lmtzr.lemmatize(word.lower(), _get_wordnet_pos(word)) for word in word_tokenize(strr)])

def get_jaccard_sim(str1, str2):
    a = set(_lemmatizeSentence(str1))
    b = set(_lemmatizeSentence(str2))
    c = a.intersection(b)
    return round(float(len(c)) / (len(a) + len(b) - len(c)),4)


# # baaler metric.

# !pip install editdistance
import editdistance

def levenshtein_distance_score(reference_txt: str, generated_txt: str):
    return round(editdistance.eval(reference_txt.split(), generated_txt.split()), 4)
