#-----# Importing packages #-----#

import argparse
import re

from pathlib import Path
import pandas as pd
import numpy as np

#-----# Project desctiption #-----#

# Basic python scripting using object-oriented coding - word collocation
'''
Using the corpus called 100-english-novels, write a Python programme which does the following:

- The script should take a directory of text files, a keyword, and a window size (number of words) as input parameters, and an output file called out/{filename}.csv
- Find out how often each word collocates with the target across the corpus
- Use this to calculate mutual information between the target word and all collocates across the corpus
- Save result as a single file consisting of three columns: collocate, raw_frequency, MI
''' 

'''
Shortcomings of this script:
- The current function concatenates all text files before calculating relevant scores. Therefore, the 'window' slides across the boundaries of each text which is not optimal.
'''

#-----# Defining main function #-----#

def main(args):
    
    # Initialising arguments that can be specified in command line
    keyword = args.key
    
    window_size = args.ws

    data_folder = args.df


    Collocation(keyword=keyword, window_size=window_size, data_folder=data_folder)

#-----# Defining class #-----#

# Setting class 'CountFunctions'
class Collocation:

    def __init__(self, keyword, window_size, data_folder):

        # Defining keyword as the parsed argument 'keyword' as a self-variable
        self.keyword = keyword 

        # Defining keyword as the parsed argument 'window_size' as a self-variable
        self.window_size = window_size 

        # Set default data dir if none is given
        self.data_dir = self.setting_data_directory(data_folder) 
        
        # Setting output directory for the generated csv file
        self.out_dir = self.setting_output_directory() 

        # Getting list of filepaths for the images
        files = self.get_paths_from_data_directory(self.data_dir) 

        # Getting tokenized version off concatenated text corpus
        tokenized_text = self.get_tokenized_concatenated_texts(files) 

        # Getting list of unique collocatess
        collocates, R1 = self.get_list_of_collocates(tokenized_text, self.keyword , self.window_size)  

        # Empty list for raw frequencies of collocates
        raw_frequencies = [] 
        
        # Empty list for MI-scores between keyword and collocate for all collocates
        MIs = [] 

        # Loop through collocates
        for collocate in collocates: 
            
            # Raw frequency of collocate
            collocate_raw_frequency = self.get_raw_frequency(tokenized_text, collocate)  

            # Joint frequency of keyword and collocate
            O11 = self.get_O11(tokenized_text, self.keyword, collocate, self.window_size)  

            # Calculating C1: Same as raw frequency of collocate
            C1 = collocate_raw_frequency  

            # O11 + O12 + O21 + O22
            N = len(tokenized_text)  

            # Expected frequencys
            E11 = (R1 * C1 / N)  
            
            # Calculating Mutual information
            MI = np.log2(O11 / E11)  

            # Adding information for given collocate to lists
            raw_frequencies.append(collocate_raw_frequency) 

            MIs.append(MI)

        # Gathering needed lists into a dictionary
        data_dict = {"collocate": collocates, 
                     "raw_frequency": raw_frequencies,
                     "MI": MIs}

        # Creating pd data frame from dictionary
        df = pd.DataFrame(data=data_dict)
        
        # Sorting collocates with highest frequency at the top.
        df = df.sort_values("MI", ascending=False)  

        # Path for csv file with unique name
        write_path = self.out_dir / f"{self.keyword}_collocates_ws_{self.window_size}.csv" 

        # Writing csv files
        df.to_csv(write_path) 


    #-#-# UTILITY FUNCTIONS #-#-#  

    # Defining function for setting directory for the raw data
    def setting_data_directory(self, data_folder):

        root_dir = Path.cwd()  # Setting root directory

        data_dir = root_dir / 'data' / data_folder # Setting data directory

        return data_dir


    # Defining function for setting directory for the output
    def setting_output_directory(self):

        root_dir = Path.cwd()  # Setting root directory

        out_dir = root_dir / 'output' # Setting output directory

        return out_dir
    

    # Defining function for obtaining individual filepaths for data files
    '''
    Creates a list containing paths to filenames in a data directory
    Args:
        data_dir: Path to the data directory.
    Returns:
        files (list): List of individual file paths
    '''
    def get_paths_from_data_directory(self, data_dir):
        
        # Creating empty list
        files = [] 

        # Loop for iterating through all files in the directory and append individual file paths to the empty list files
        for file in data_dir.glob('*.txt'): 

            files.append(file)

        return files


    # Defining function for finding all unique collocate
    '''
    Creates a list of unique collocates for the specific keyword
    Args:
        tokenized_text (string): Tokenised version of full text corpus
        keyword (string): Specified keyword
        collocate (string): Specified collocate of the keyword
        window_size (integer): Specified window size in which to search for collocates
    Returns:
        unique_collocates (list): List of unique collocates
        R1 (int) : Number of possible pairs with key (number of collocates)
    '''
    def get_list_of_collocates(self, tokenized_text, keyword, window_size):

            # Create empty list for all collocate
            collocates = [] #

            for i, word in enumerate(tokenized_text):
                
                # If keyword is detected, generate a window around it and extract collocates (words in the window)
                if word == keyword:

                    left_window = tokenized_text[max(0, i - window_size):i]

                    right_window = tokenized_text[i+1:(i + window_size)]

                    total_window = left_window + right_window

                    # Add all collocates from window to the full list of collocates
                    collocates.extend(total_window) 
            
            # Only keep one of each unique collocate
            unique_collocates = pd.unique(collocates)

            # Number of all collocates in each window combined 
            R1 = len(collocates) 

            return unique_collocates, R1


    # Defining function for counting raw frequency of a word in the tokensied text corpus
    '''
    Generates a count of the word frequency in the coprus for a given word
    Args:
        tokenized_text (list): Tokenised version of full text corpus
    Returns: 
        word_frequency (integer): Count of word frequency
    '''
    def get_raw_frequency(self, tokenized_text, focus_word):
        
        # Start counter at zero
        word_frequency = 0

        # Loop through all tokenised words and count number of times word is found
        for word in tokenized_text:

            if word == focus_word:

                word_frequency += 1

        return word_frequency
    

    # Defining function for getting frequency of keyword and collocate appearing together
    '''
    Creates a count of the  frequency of keyword and collocate appearing together
    Args:
        tokenized_text (string): Tokenised version of full text corpus
        keyword (string): Specified keyword
        collocate (string): Specified collocate of the keyword
        window_size (integer): Specified window size in which to search for collocates
    Returns:
        O11 (integer): O11 value for the specified keyword and collocate
    '''
    def get_O11(self, tokenized_text, keyword, collocate, window_size):

        # Stat counter at zero
        O11 = 0

        # Loop through tokens
        for i, word in enumerate(tokenized_text):

                # Record all instances of keyword and create a window around it
                if word == keyword: 
                    
                    # Cannot go beyond first word
                    left_window = tokenized_text[max(0, i - window_size):i]

                    right_window = tokenized_text[i+1:(i + window_size)]

                    total_window = left_window + right_window

                    # Count how many times (if any) collocate is in list
                    collocate_count = total_window.count(collocate)

                    O11 += collocate_count

        return O11


    # Defining function for opening and reading text files
    '''
    Loads and reads a txt file
    Args:
        file: A path to an image file.
    Returns:
       text (string): Text of a txt file
    '''
    def load_text(self, file):

        # Read each .txt file
        with open(file, encoding="utf-8") as file:

            text = file.read()
            
            # Using lowercase method to set all characters to lowercase
            text = text.lower() 

            file.close()

        return text


    # Defining tokeniser function
    '''
    Tokenizes an input text:
    Args:
        input_text (string): Input text
    Returns:
        tokenized_text (list): List of individual tokens
    '''
    def tokenize(self, input_text):

        # Split on any non-alphanumeric character
        tokenizer = re.compile(r"\W+")

        # Tokenize
        tokenized_text = tokenizer.split(input_text) 

        # Return token list
        return tokenized_text


    # Defining function for concatenating .txt files into one text    
    '''
    Creates a combined tokenised text from multiple files
    Args:
        files (list) : List of file paths
    Returns:
        text_corpus (string) : Full tokenised text
    '''
    def get_tokenized_concatenated_texts(self, files):

        # Empty list for full tokenized text corpus
        tokenized_text_corpus = []

        for file in files:
            
            # Load text
            text = self.load_text(file)

            # Use tokenizer to toxenize text
            tokenized_text = self.tokenize(text)

            # Append tokenized text to full corpus list
            tokenized_text_corpus.extend(tokenized_text)

        return tokenized_text_corpus


# Executing main function when script is run
if __name__ == '__main__':

    #Create an argument parser from argparse
    parser = argparse.ArgumentParser(description = "[INFO] Calculating Word Collocation Mutual Information Scores",
                                formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-key', 
                        metavar="--keyword",
                        type=str,
                        help=
                        "[DESCRIPTION] The name of the desired keyword\n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     cat \n"
                        "[EXAMPLE]     -key cat \n",
                        required=False,
                        default='cat')

    parser.add_argument('-ws', 
                        metavar="--window_size",
                        type=int,
                        help=
                        "[DESCRIPTION] How many words the sliding window \n"
                        "              should extend on both sides of the keyword \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     2 \n"
                        "[EXAMPLE]     -ws 2 \n",
                        required=False,
                        default=2)
        
    parser.add_argument('-df', 
                        metavar="--data_folder",
                        type=str,
                        help=
                        "[DESCRIPTION] Name of folder with desired data (needs to be in data folder) \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     100_enlgish_novels \n"
                        "[EXAMPLE]     -df 100_enlgish_novels \n",
                        required=False,
                        default='100_enlgish_novels')
        

    main(parser.parse_args())