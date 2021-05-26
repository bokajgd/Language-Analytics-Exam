#-----# Importing packages #-----#

# System / setup 
import argparse

# Data analysis packages
from pathlib import Path
import pandas as pd

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

    # Initialising classs
    LDAFeats2Classification(pos_data=pos_data, neg_data=neg_data)

#-----# Defining class #-----#

class LDAFeats2Classification:

    def __init__(self):
        #-----# Preprocessing data #-----#
        # Load data

        # Get labels

        # Split data

        #-----# LDA Feature Extraction #-----#

        # Train LDA model

        #-----# Train classifier #-----#

        # Train logistic regression

        #-----# Evaluation #-----#

        # Test data through LDA model

        # Perhaps visualisations

    
    #-----# Utility functions #-----#

# Executing main function when script is run from command line
if __name__ == '__main__':

    #Create an argument parser from argparse
    parser = argparse.ArgumentParser(description = "[INFO] Pre-processing discharge summaries",
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
    
    main(parser.parse_args())