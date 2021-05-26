#-----# Importing packages #-----#

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import argparse
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn import metrics


#-----# Project desctiption #-----#

'''
This script trains a logistic regression classifier on the cleaned tf-idf vectorised notes 
producted by the data_preprocessing.py script and tests it's ability to predict unplanned readmissions within 30-days
'''

#-----# Defining main function #-----#

# Defining main function
def main(args):

    train_data = args.tr

    test_data = args.te

    train_labels = args.trl

    test_labels = args.tel

    ReadmissionPrediction(train_data = train_data, 
                          test_data = test_data,
                          train_labels = train_labels,
                          test_labels = test_labels)

#-----# Defining class #-----#

class ReadmissionPrediction:

    def __init__(self, train_data, test_data, train_labels, test_labels):
        
        # Setting directory of input data 
        self.data_dir = self.setting_data_directory() 

        # Setting directory of output plots
        self.out_dir = self.setting_output_directory() 

        # Loading training data
        if train_data is None:

            self.train_data = self.load_data(file_name='tfidf_train_notes.csv') 

        else:

            self.train_data = self.load_data(file_name=train_data) 

        # Loading test data 
        if test_data is None:

            self.test_data = self.load_data(file_name='tfidf_test_notes.csv')

        else:

            self.test_data = self.load_data(file_name=test_data) 

        # Load training labels
        if train_labels is None:

            self.train_labels = self.load_data(file_name='train_labels.csv')
            
        else:
            self.train_labels = self.load_data(file_name=train_labels)

        # Load training labels
        if test_labels is None:

            self.test_labels = self.load_data(file_name='test_labels.csv')

        else:

            self.test_labels = self.load_data(file_name = test_labels)

        # Run logistic regression and print results
        self.logistic_regression()

        # Generate auc_roc curve
        self.plot_auc_roc()

        # Rank features by importance
        importance = self.get_most_important_features(self.lr, 20)

        # Get most important features
        top_scores = [a[0] for a in importance[0]['tops']]
        top_words = [a[1] for a in importance[0]['tops']]
        bottom_scores = [a[0] for a in importance[0]['bottom']]
        bottom_words = [a[1] for a in importance[0]['bottom']]

        # Generate bar plot
        self.plot_important_words(top_scores, top_words, bottom_scores, bottom_words, "Most important words for predicting unplanned readmission")


    #-#-# FUNCTION LOGISTIC REGRESSION #-#-#
    '''
    '''
    def logistic_regression(self):

        # Fitting and training the model
        self.lr = LogisticRegression(penalty='l2', 
                            tol=0.0001, 
                            solver='saga', 
                            multi_class='multinomial').fit(self.train_data, np.ravel(self.train_labels))

        # Evaluating the model
        test_preds = self.lr.predict(self.test_data)

        # Getting metrics 
        cm = metrics.classification_report(self.test_labels, test_preds)

        print(cm)

    #-#-# UTILITY FUNCTIONS #-#-#  

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


    # Load data function
    def load_data(self, file_name):

        # Load data
        data = pd.read_csv(self.out_dir / file_name) 

        # Remove first column
        data = data.drop(data.columns[0], axis=1) 
        
        # Convert to np array
        data = data.to_numpy() 

        return data


    # Code for this function was modified from here: https://machinelearningmastery.com/roc-curves-and-precision-recall-curves-for-classification-in-python/
    '''
    '''
    def plot_auc_roc(self):
        
        # Generate a no skill prediction (majority class)
        ns_probs = [0 for _ in range(len(self.test_labels))]
        
        # Rredict probabilities
        lr_probs = self.lr.predict_proba(self.test_data)

        # Keep probabilities for the positive outcome only
        lr_probs = lr_probs[:, 1]

        # Calculate roc-auc scores
        ns_auc = metrics.roc_auc_score(self.test_labels, ns_probs)

        lr_auc = metrics.roc_auc_score(self.test_labels, lr_probs)

        # Summarise and print scores
        print('No Skill: ROC AUC=%.3f' % (ns_auc))
        
        print('Logistic: ROC AUC=%.3f' % (lr_auc))

        # Calculate roc curves
        ns_fpr, ns_tpr, _ = metrics.roc_curve(self.test_labels, ns_probs)
        
        lr_fpr, lr_tpr, _ = metrics.roc_curve(self.test_labels, lr_probs)
        
        # Plot the roc curve for the model
        plt.plot(ns_fpr, ns_tpr, linestyle='--', label='No Skill', color='#3D4F82')

        plt.plot(lr_fpr, lr_tpr, marker='.', label='Logistic', color='#3D4F82')

        # Axis labels
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')

        # Show the legend
        plt.legend()
        # Save the plot
        plt.savefig(Path.cwd() / 'viz' / 'ROC-AUC.png')


    # Following functions were obtained from: https://colab.research.google.com/drive/11veImdUwDtXs7H_NjnNRunpybRfgPOTI#scrollTo=7WEtOIF41QtL
    def get_most_important_features(self, model, n=5):

        # Load in vocabualry
        vocab = np.load(self.out_dir / 'vocab' / 'vocabulary.pkl', allow_pickle=True)

        index_to_word = {v:k for k,v in vocab.items()}
        
        # Loop for each class
        classes ={}

        for class_index in range(model.coef_.shape[0]):
            
            word_importances = [(el, index_to_word[i]) for i,el in enumerate(model.coef_[class_index])]

            sorted_coeff = sorted(word_importances, key = lambda x : x[0], reverse=True)

            tops = sorted(sorted_coeff[:n], key = lambda x : x[0])

            bottom = sorted_coeff[-n:]
            
            classes[class_index] = {
                'tops':tops,
                'bottom':bottom
            }

        return classes

    # Plot bar plot of most important words
    def plot_important_words(self, top_scores, top_words, bottom_scores, bottom_words, name):

        y_pos = np.arange(len(top_words))

        top_pairs = [(a,b) for a,b in zip(top_words, top_scores)]

        top_pairs = sorted(top_pairs, key=lambda x: x[1])
        

        bottom_pairs = [(a,b) for a,b in zip(bottom_words, bottom_scores)]

        bottom_pairs = sorted(bottom_pairs, key=lambda x: x[1], reverse=True)
        

        top_words = [a[0] for a in top_pairs]

        top_scores = [a[1] for a in top_pairs]
        
        bottom_words = [a[0] for a in bottom_pairs]

        bottom_scores = [a[1] for a in bottom_pairs]
        
        fig = plt.figure(figsize=(10, 10))  

        plt.subplot(121)

        plt.barh(y_pos,bottom_scores, align='center', alpha=0.8, color='#3D4F82')

        plt.title('No Readmission', fontsize=20)

        plt.yticks(y_pos, bottom_words, fontsize=11)

        plt.suptitle('Key words', fontsize=16)

        plt.xlabel('Importance', fontsize=20)
        
        plt.subplot(122)

        plt.barh(y_pos,top_scores, align='center', alpha=0.8, color='#3D4F82')

        plt.title('Readmission', fontsize=20)

        plt.yticks(y_pos, top_words, fontsize=11)

        plt.suptitle(name, fontsize=16)

        plt.xlabel('Importance', fontsize=20) 
        
        plt.subplots_adjust(wspace=0.8)

        # Save figure
        plt.savefig(Path.cwd() / 'viz' / 'most_important.png', bbox_inches='tight', pad_inches=2) 


# Executing main function when script is run
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-tr', 
                        metavar="--train_data",
                        type=str,
                        help=
                        "[DESCRIPTION] The file name of the training data csv \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     tfidf_train_notes.csv \n"
                        "[EXAMPLE]     -tr tfidf_train_notes.csv \n",
                        required=False)

    parser.add_argument('-te', 
                        metavar="--test_data",
                        type=str,
                        help=
                        "[DESCRIPTION] The file name of the test data csv \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     tfidf_test_notes.csv \n"
                        "[EXAMPLE]     -tr tfidf_test_notes.csv \n",
                        required=False)

    parser.add_argument('-trl', 
                        metavar="--train_labels",
                        type=str,
                        help=
                        "[DESCRIPTION] The file name of the training labels csv\n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     train_labels.csv \n"
                        "[EXAMPLE]     -tr train_labels.csv \n",
                        required=False)

    parser.add_argument('--tel', 
                        metavar="--test_labels",
                        type=str,
                        help=
                        "[DESCRIPTION] The file name of the test labels csv\n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     test_labels.csv \n"
                        "[EXAMPLE]     -tr test_labels.csv \n",
                        required=False)


    main(parser.parse_args())