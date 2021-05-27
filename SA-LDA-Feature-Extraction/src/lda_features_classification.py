#-----# Importing packages #-----#

# System / setup 
import argparse

# Data analysis packages
from pathlib import Path
import pandas as pd
import numpy as np
import string
import matplotlib.pyplot as plt

import gensim

# For tokenisation
import nltk
from nltk import word_tokenize
nltk.download('punkt')

# TF-IDF vectoriser
from sklearn.feature_extraction.text import CountVectorizer

# LogReg functions
from sklearn.linear_model import LogisticRegression
from sklearn import metrics


#-----# Project desctiption #-----#

# Extracting Latent Feature Representations using LDA for use as Inputs in Supervised Text Classification
'''
'''

#-----# Defining main function #-----#

# Defining main function
def main(args):

    # Initialising arguments that can be specified in command line
    pos_data = args.pd

    neg_data = args.nd

    max_features = args.mf

    ngram_range = args.ng

    chunksize = args.ch

    passes = args.pa

    # Initialising classs
    LDAFeats2Classification(pos_data=pos_data,
                            neg_data=neg_data,
                            max_features=max_features,
                            ngram_range=ngram_range,
                            chunksize=chunksize,
                            passes=passes)

#-----# Defining class #-----#

class LDAFeats2Classification:

    def __init__(self, pos_data, neg_data, max_features, ngram_range, chunksize, passes):

        # Setting directory of input data 
        self.data_dir = self.setting_data_directory() 

        # Setting directory of output plots
        self.out_dir = self.setting_output_directory() 

        #-----# Preprocessing data #-----#
        
        # Load data

        # If pos_data is not given, default to true news data set
        if pos_data is None:

            pos_data = 'True.csv'

        true_news = pd.read_csv(self.data_dir / f'{pos_data}')

        # If neg_data is not given, default to false news data set
        if neg_data is None:

            neg_data = 'Fake.csv'

        fake_news = pd.read_csv(self.data_dir / f'{neg_data}')
        

        # Add labels
        true_news['label'] = int(1)
        
        fake_news['label'] = int(0)

        # Merge data frames 
        full_data = pd.concat([true_news, fake_news], ignore_index=True)
        
        # Shuffle data
        full_data = full_data.sample(n = len(full_data), random_state = 42) # Setting random state so results can be replicated

        full_data = full_data.reset_index(drop = True)

        # Remove new lines ('\n') and carriage returns ('\r')
        full_data.text = full_data.text.str.replace('\n',' ')
        
        full_data.text = full_data.text.str.replace('\r',' ')

        # Split data into test and train set
        train, test = self.split_data(full_data, test_frac=0.2)

        #-----# Vectorise data #-----#

        vocab, train_labels, test_labels, train_bow, test_bow = self.bow_vectorisation(train, 
                                                                                       test, 
                                                                                       max_features, 
                                                                                       ngram_range)
 
        #-----# LDA Feature Extraction #-----#

        # Transform vocab and document vectors to fit gensims functions
        train_corpus = gensim.matutils.Sparse2Corpus(train_bow, documents_columns=False)

        test_corpus = gensim.matutils.Sparse2Corpus(test_bow, documents_columns=False)
         
        # Transform vocab to dict
        id2word = dict((v, k) for k, v in vocab.items())


        # Train LDA model
        self.lda_train = gensim.models.ldamulticore.LdaMulticore(
                           corpus=train_corpus,
                           num_topics=30,
                           id2word=id2word,
                           chunksize=chunksize,
                           workers=3,
                           passes=passes,
                           eval_every=10,
                           per_word_topics=True)

        # Print words for topics
        print(self.lda_train.print_topics(20,num_words=5)[:5])

        # Transform 
        train_topic_vectors = self.get_topic_vectors(train, train_corpus)

        test_topic_vectors = self.get_topic_vectors(test, test_corpus)

        #-----# Train and test classifier #-----#
        
        # Train and test logistic regression with LDA topic vectors as inputs
        print('\n PRINTING RESULTS FOR CLASSIFIER TRAINED ON TOPIC VECTORS \n')
        
        self.logistic_regression(train_topic_vectors, 
                                 train_labels,
                                 test_topic_vectors,
                                 test_labels,
                                 'LDA-Topic-Vectors')

        # Compare to classifier trained directly on BoW vectors
        print('\n PRINTING RESULTS FOR CLASSIFIER TRAINED ON BoW VECTORS \n')

        self.logistic_regression(train_bow, 
                                 train_labels,
                                 test_bow,
                                 test_labels,
                                 'BoW-Feature-Vectors')

        # This also plots and save confusion matrixes
    
    # Defining logistic regression classifier and evaluation
    '''
    '''
    def logistic_regression(self, train_data, train_labels, test_data, test_labels, name):

        # Fitting and training the model
        lr = LogisticRegression(penalty='l2', 
                            tol=0.0001, 
                            solver='saga', 
                            multi_class='multinomial').fit(train_data, np.ravel(train_labels))

        # Evaluating the model
        test_preds = lr.predict(test_data)

        # Getting metrics 
        cr = metrics.classification_report(test_labels, test_preds)
        
        print(cr)

        # Plotting confusion matrix
        cm = metrics.plot_confusion_matrix(lr, test_data, test_labels, cmap=plt.cm.Greens, normalize='true')
        
        cm.ax_.set_title(f'Confusion Matrix for Fake News Detection \n {name}')

        plt.savefig(self.out_dir / f'{name}_confusion_matrix.png', dpi=300)
        

    # Defining function for extracting topic vectors for each document in the corpus
    def get_topic_vectors(self, df, gensim_corpus):
        
        # Empty list 
        train_vecs = []
        
        # Low throug each doc
        for i in range(len(df.index)):

            # Get topic numbers
            top_topics = self.lda_train.get_document_topics(gensim_corpus[i], minimum_probability=0.0)

            # Collect numbers into list
            topic_vec = [top_topics[i][1] for i in range(30)]

            # Append list to full list
            train_vecs.append(topic_vec)
        
        # Turn into array
        train_vecs = np.array(train_vecs)

        return train_vecs

    # Defining vectoriser functions
    def bow_vectorisation(self, train, test, max_features, ngram_range):

        # Defining BoW count vectorizer 
        vect = CountVectorizer(max_features = max_features, 
                            tokenizer = self._tokenizer_better, 
                            stop_words = 'english',
                            ngram_range = (1,ngram_range), # Include uni-, bi- or trigrams
                            max_df = 0.8)

        # Fit vectorizer to discharge notes
        vect.fit(train.text.values)

        # Transform our notes into numerical matrices
        train_data = vect.transform(train.text.values)

        test_data = vect.transform(test.text.values)

        # Saving training data vocabulary
        vocab = vect.vocabulary_

        # Saving seperate variables containing classification labels
        train_labels = train.label

        test_labels = test.label

        return vocab, train_labels, test_labels, train_data, test_data

    # Defining function for splitting data into a train and a test set
    '''
    '''
    def split_data(self, full_data, test_frac):

        # Save 20% of the data as test data 
        test = full_data.sample(frac=test_frac, random_state=42)

        # Use the rest of the data as training data
        train = full_data.drop(test.index)

        return train, test

    #-----# Utility functions #-----#
    
        # Defining function for setting directory for the raw data
    def setting_data_directory(self):
        
        # Setting root directory
        root_dir = Path.cwd()  

        # Setting data directory
        data_dir = root_dir / 'data' 

        return data_dir


    # Defining function for setting directory for the output
    def setting_output_directory(self):
        
        # Setting root directory
        root_dir = Path.cwd()

        # Setting output directory
        out_dir = root_dir / 'output' 

        return out_dir
    

    # Define a tokenizer function
    def _tokenizer_better(self, text):    

        # Define punctuation list
        punc_list = string.punctuation+'0123456789'

        t = str.maketrans(dict.fromkeys(punc_list, ''))

        # Remove punctuaion
        text = text.lower().translate(t)

        # Tokenise 
        tokens = word_tokenize(text)

        return tokens


# Executing main function when script is run from command line
if __name__ == '__main__':

    #Create an argument parser from argparse
    parser = argparse.ArgumentParser(description = "[INFO] Feature Extraction using LDAs",
                                formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-pd', 
                        metavar="--positive_data",
                        type=str,
                        help=
                        "[DESCRIPTION] The path for the file containing data for positive instances (true news stories). \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     True.csv \n"
                        "[EXAMPLE]     -pd True.csv \n",
                        required=False)

    parser.add_argument('-nd', 
                        metavar="--negative_data",
                        type=str,
                        help=
                        "[DESCRIPTION] The path for the file containing data for negative instances (false news stories) \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     False.csv \n"
                        "[EXAMPLE]     -nd FALSE.csv \n",
                        required=False)
    
    parser.add_argument('-mf',
                        metavar="--max_features",
                        type=int,
                        help=
                        "[DESCRIPTION] The number of features to keep in the vectorised notes \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     30000 \n"
                        "[EXAMPLE]     -mf 30000 \n",
                        required=False,
                        default=30000)

    parser.add_argument('-ng',
                        metavar="--ngram_range",
                        type=int,
                        help=
                        "[DESCRIPTION] Defines the range of ngrams to include (either 2 or 3) \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     3 \n"
                        "[EXAMPLE]     -ng 3 \n",
                        required=False,
                        default=3)

    parser.add_argument('-ch',
                        metavar="--chunksize",
                        type=int,
                        help=
                        "[DESCRIPTION] The number of documents per chunk when training the LDA model \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     200 \n"
                        "[EXAMPLE]     -ch 200 \n",
                        required=False,
                        default=200)

    parser.add_argument('-pa',
                        metavar="--passes",
                        type=int,
                        help=
                        "[DESCRIPTION] The number of 'itereations' LDA training should run for \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     10 \n"
                        "[EXAMPLE]     -pa 10 \n",
                        required=False,
                        default=10)


    main(parser.parse_args())