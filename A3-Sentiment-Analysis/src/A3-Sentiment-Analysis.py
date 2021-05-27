#-----# Importing packages #-----#

import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

#-----# Project desctiption #-----#

# Basic python scripting using object-oriented coding
'''
Calculate the sentiment score for every headline in the data. 
Create and save a plot of sentiment over time with a 1-week rolling average
Create and save a plot of sentiment over time with a 1-month rolling average
Make sure that you have clear values on the x-axis and that you include the following: a plot title; labels for the x and y axes; and a legend for the plot
Write a short summary (no more than a paragraph) describing what the two plots show. You should mention the following points: 
1) What (if any) are the general trends? 2) What (if any) inferences might you draw from them?
'''

#-----# Defining main function #-----#

# Defining main function 
def main(args):

    # Adding argument that can be specified in command line
    filename = args.fn 

    # Calling main class 
    SentimentAnalysis(filename=filename) 


#-----# Defining class #-----#

class SentimentAnalysis:

    def __init__(self, filename):
        
        # Setting directory of input data
        self.data_dir = self.setting_data_directory() 
         
        # Setting directory of output plots 
        self.out_dir = self.setting_output_directory()

        # Setting filename as the provided filename
        self.filename = filename 

        # If no filename is not specified, use test_data.csv as default file
        if self.filename is None: 

            self.filename = "abcnews-date-text_subset.csv"

        # Read csv file
        df = pd.read_csv(self.data_dir / f'{self.filename}')  
        
        # Adding a column with calculated polarity scores for each headline
        df["polarity"] = self.get_polarity_score(text = df["headline_text"]) 

        # Converting publish data columnt to datetime
        df['publish_date'] =  pd.to_datetime(df['publish_date'], format='%Y%m%d')

        # Deleting column with text
        del df['headline_text']
        
        # Grouping by different periods 
        df_grouped_daily = self.group_data(df, 'd')

        self.df_grouped_yearly = self.group_data(df, 'y')

        # Generating and saving plot of 7-day rolling average sentiment score
        self.create_plot(data = df_grouped_daily, rolling = 7, plot_name = "Weekly_Rolling_Average_Polarity") 

        # Generating and saving plot of 30-day rolling average sentiment score
        self.create_plot(data = df_grouped_daily, rolling = 30, plot_name = "Monthly_Rolling_Average_Polarity") 


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
    

    # Defining function for calculating polarity
    '''
    Generates a list containing a polarity score for each input
    Args:
        text: Input text
    Returns:
        polarity (list): List containing polarity scores for each headline
    '''
    def get_polarity_score(self, text):

        # Loading spaCy model
        nlp = spacy.load("en_core_web_sm") 

        # Initialise spaCyTextBlob 
        spacy_text_blob = SpacyTextBlob()   

        # Add spaCyTextBlob as a new component to our spaCy nlp pipeline  
        nlp.add_pipe(spacy_text_blob) 

        # Creating empy list for scores
        polarity = [] 

        # Loop through each headline and calculate polarity score
        for headline in nlp.pipe(text): 

            polarity_score = headline._.sentiment.polarity 
            
            # Append score to list
            polarity.append(float(polarity_score)) 

        return polarity


    # Defining function for creating a plot of development in sentiment scores 
    '''
    Generates and save a matplotlib plot showing time series development in polarity scores
    Args:
        data (pd.df) : Input data frame of polarity scores grouped after according to time interval
        rolling (iny) : How many days to calculate roling average over
        plot_name (str) : Name of plot both for file name and title
    '''
    def create_plot(self, data, rolling, plot_name):
        
        # Plot data
        fig, ax = plt.subplots(1, 1, dpi=300) 

        # Plot lines
        ax.plot(data['polarity'].rolling(rolling).mean(), label="Rolling Average Polarity", color = "#3E5B75") 

        ax.plot(self.df_grouped_yearly['polarity'], label="Yearly Average Polarity", color = "#E09D1E") 

        # Define a title
        plt.title(plot_name) 

        # Define legend position
        plt.legend(loc='upper right') 

        # Define x-axis label
        plt.xlabel('Date')  

        # Define y-axis label
        plt.ylabel('Polarity')

        # Rotate xticks
        fig.autofmt_xdate()

        # Define output path using out_dirs
        path = self.out_dir / f"{plot_name}.png" 
        
        # Save figure
        plt.savefig(path) 

        plt.close()


    # Defining function for grouping data by period
    '''
    Returns a data frame that has been grouped by specified period
    Args:
        df (pd.df) : Input data with polarity scores and data columns
        period (str) : Period on which to group by (e.g. 'w' for week)
    Returns:
        grouped_df (pd.df): Grouped data frame
    '''
    def group_data(self, df, period):
        
        # Group by period
        df_grouped = df.groupby(df['publish_date'].dt.to_period(period)).mean()

        # Return index to dates for xticks later 
        df_grouped.index = df_grouped.index.to_timestamp()
        
        return df_grouped


# Executing main function when script is run
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "[INFO] Sentiment Analysis on a Million Headlines",
                                formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-fn', 
                        metavar="--filename",
                        type=str,
                        help=
                        "[DESCRIPTION] The name of the input data file \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     abcnews-date-text_subset.csv \n"
                        "[EXAMPLE]     -fn abcnews-date-text_subset.csv \n",
                        required=False)
    
    parser.add_argument('-dd', 
                        metavar="--data_directory",
                        type=str,
                        help=
                        "[DESCRIPTION] Path to directory where data is located \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     A3-Sentiment-Analysis/data \n"
                        "[EXAMPLE]     -dd A3-Sentiment-Analysis/data \n",
                        required=False)

    main(parser.parse_args())