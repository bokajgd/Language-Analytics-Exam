#-----# Importing packages #-----#

# System / setup 
import argparse

# Data analysis packages
from pathlib import Path
import pandas as pd
from collections import Counter
from itertools import combinations 
from tqdm import tqdm
import matplotlib.pyplot as plt
import networkx as nx

# NLP packages
import spacy
nlp = spacy.load("en_core_web_sm")

#-----# Project desctiption #-----#

# Network analysis using object-oriented framework
'''
[TASK DESCRIPTION]
Your script should be able to be run from the command line
It should take any weighted edgelist as an input, providing that edgelist is saved as a CSV with the column headers "nodeA", "nodeB"
For any given weighted edgelist given as an input, your script should be used to create a network visualization, which will be saved in a folder called viz.
It should also create a data frame showing the degree, betweenness, and eigenvector centrality for each node. It should save this as a CSV in a folder called output.

[ADDITIONS]
The script is able to take either a pre-produced edge file or a csv file containing a text column from which it generates an edge file by finding co-occurences of 
for the entities extracted from the text. Which entities to extract using NER can be determined by the user (e.g. LOC, PERSON, ORG)
'''

#-----# Defining main function #-----#
def main(args):

    # Adding arguments that can be specified in command line
    text_file = args.tf

    edge_file = args.ef

    n_edges = args.ne 

    tag = args.tg

    identifier = args.id

    # Initialising class
    NetworkAnalysis(n_edges=n_edges, tag=tag, text_file=text_file, edge_file=edge_file, identifier=identifier)  # Calling main class 

#-----# Defining class #-----#
class NetworkAnalysis:

    #-----# Defining __init__ method #-----#
    def __init__(self,  n_edges, tag, text_file=None, edge_file=None, identifier=None):

        # Setting directory of input data 
        data_dir = self.setting_data_directory() 

        # Setting directory of output plots
        out_dir = self.setting_output_directory() 

        # Setting filename of edge file as the provided edge file filename
        self.text_file = text_file 

        # Setting filename of edge file as the provided edge file filename
        self.edge_file = edge_file 
        
        # Setting number of nodes to be kept
        self.n_edges = n_edges 
        
        # Setting tag of entities to extract
        self.tag = tag

        # Setting identifier for use in naming output files
        self.identifier = identifier

        # If both text_file and edge_file args are none, set edge_file to example file provided in folder
        if text_file is None and edge_file is None:

            self.edge_file = "edges_df.csv"

        # If text file is given then generate and edge file 
        if text_file is not None: 
            
            # If identifier is not given, set it as the first part if text_file
            if identifier is None:

                # Remove last 4 characters to remove '.csv'
                self.identifier = str(self.text_file)[:len(self.text_file)-4]

            # Read csv text file
            text_csv = pd.read_csv(data_dir / 'text_files' / f'{self.text_file}')

            # Generate list of entities extracted from each document in text file
            entities = self.get_entities(text_file=text_csv, tag=self.tag)

            # Get list of list all possible edges for each document
            edgelist = self.get_edges(entities=entities)

            # Generate edge file
            generated_edge_file = self.get_edge_file(edgelist=edgelist, data_dir=data_dir)

            # Creating network graph using pre-defined graphing function
            graph = self.get_network_graph(edge_file=generated_edge_file, n_edges=self.n_edges, loaded=False)

            # Calculating nodes metrics and saving df
            self.get_centrality_df(graph, out_dir=out_dir)

        # If text file is none, use edge_file passed in command line (or default if none)
        else:
            
            # If identifier is not given, set it as the first part if edge_file
            if identifier is None:

                # Remove last 4 characters to remove '.csv'
                self.identifier = str(self.edge_file)[:len(self.edge_file)-4]

            # Read csv edge file
            edge_csv = pd.read_csv(data_dir / 'edge_files' / f'{self.edge_file}')

            # Creating network graph using pre-defined graphing function
            graph = self.get_network_graph(edge_file=edge_csv, n_edges=self.n_edges, loaded=True)

            # Calculating nodes metrics and saving df
            self.get_centrality_df(graph, out_dir=out_dir)


    #-----# Defining utility functions used in the __init__ #-----#

    # Defining function for setting directory for the raw data
    def setting_data_directory(self):

        root_dir = Path.cwd()  # Setting root directory

        data_dir = root_dir / 'data'   # Setting data directory

        return data_dir


    # Defining function for setting directory for the output
    def setting_output_directory(self):

        root_dir = Path.cwd()  # Setting root directory

        out_dir = root_dir / 'output' # Setting output directory

        return out_dir

    # Defining function for creating and saving df containing degree, betweenness, and eigenvector centrality scores for all nodes in the network
    '''
    Generates a list of lists of entities for each row in passed text csv file
    Args:
        text_file (csv): CSV file containing a column for texts named 'text'
        tag (str) : Tag for SpaCY NER - determines which entities in the text are analysed, e.g. LOC or PERSON
        out_dir (Posix path) : Path for output
    Returns:
        all_entities (list) : List of lists of entities for each document (row) in the 'text' column of the passed text file
    '''
    def get_entities(self, text_file, tag):
        
        # Print status to command line
        print(f'\n EXTRACTING ENTITIES WITH TAG: {self.tag} \n')

        # Create list for all entities for each individual row in df
        all_entities = []

        # Loop through each row of text column in text file df
        for text in tqdm(text_file['text']):

            # Create temporary list for each individual row
            individual_entities = []

            # Create doc object
            doc = nlp(text)

            # Loop through every named entity
            for entity in doc.ents:

                # If that entity has the same tag as the given tag argument, then append to list of entities for this row
                if entity.label_ == str(tag):

                    individual_entities.append(entity.text)

            # Append ents for individual row to a all_entities list
            all_entities.append(individual_entities)
        
        return all_entities

    
    # Defining function for getting list of unique edges
    '''
    Generates a list of all node pairs (edges)
    Args:
        entities (list) : List of list of entities for each row in passed text csv file
    Returns:
        edgelist (list) : List of all node pairs (edges) created by combining the extracted entities for each document into all possible pairs
    '''
    def get_edges(self, entities):
        
        # Create list for uniqe edges
        edgelist = []
        
        # Loop through each individual list in the passed list of lists of extracted entities
        for text in entities:

            # Use itertools.combinations() to create all possible combinations of two nodes
            edges = list(combinations(text, 2))

            # Loop through unique edges 
            for edge in edges:

                # Sort node-pairs alphabetticaly (to make sure each pair is only represented once) and append to final edgelist
                edgelist.append(tuple(sorted(edge)))
            
        return edgelist


    # Defining function for generating edge file of all edges between nodes and a weight column
    '''
    Generates a an edge file with the columns 'nodeA', 'nodeB', 'weight'  from an list of unique edges and a list of all extracted entities each document
        edgelist (list) : List of all node pairs (edges) created by combining the extracted entities for each document into all possible pairs
        out_dir (Posix path) : Path for output
    Returns:
        edge_file_df (Pandas.DataFrame) : Edge file in a pd data frame format containing the following columns: 'nodeA', 'nodeB', 'weight
    '''
    def get_edge_file(self, edgelist, data_dir):
        
        # Create list for counts for each edges
        counted_edges = []

        # Loop through unique edges on edgelist  - use Counter() to bundle and count frequency of each unique edge
        for key, value in Counter(edgelist).items():

            # Get first entity
            source = key[0]

            # Get second
            target = key[1]

            # Get 'weight' score as the value output by Count() function
            weight = value

            # Append nodes and weight as a list to the empty list
            counted_edges.append((source, target, weight))

        # Convert to data frame
        edge_file_df = pd.DataFrame(counted_edges, columns=["nodeA", "nodeB", "weight"])

        # Save edge file to data folder
        df_path = data_dir / 'edge_files' / f'{self.identifier}_edge_file.csv'

        edge_file_df.to_csv(df_path) 

        return edge_file_df

    # Defining function for generating plot of network
    '''
    Generates a network graph from an edge file containing a specified number of edges
    Args:
        edge_file (pd datatframe): Edge file in a pd data frame format containing the following columns: 'nodeA', 'nodeB', 'weight
        n_edges (integer): Number of edges to keep 
        out_dir (Posix path) : Path for output
        loaded (bool) : Boolean variable to assert whether edge file has been loaded in from folder or generated in the script
    Returns:
        graph: Final network graph

    '''
    def get_network_graph(self, edge_file, n_edges, loaded):
        
        # Selecting only the desired number of edges with the highest weight scores 
        filtered_df = edge_file.sort_values('weight', ascending = False).head(n_edges) # Contrary to setting a min_edge_weight, this method can be applied to all datasets 
        
        # If edge file has been loaded using pd.read_csv then
        if loaded is True:

            # Deleting extra column generated by previous line 
            del filtered_df["Unnamed: 0"]

        # Generating network graph
        plt.figure(figsize=(10,5))

        ax = plt.gca()

        # Setting title of graph
        if loaded is not True:

            # If edge file is generated via text file input
            ax.set_title(f'Network Graph for {self.identifier} text data \n Showing top {n_edges} edges with highest weight')

        else:

            # If pre-made edge file is given as script input
            ax.set_title(f'Network Graph for {self.identifier} \n Showing top {n_edges} edges with highest weight')

        # Creating graph from edgelist
        graph = nx.from_pandas_edgelist(filtered_df, 'nodeA', 'nodeB', ["weight"])        

        # Use draw_shell visualisation
        pos = nx.draw_shell(graph,
                            with_labels = True, 
                            # Weighting the width of the edges by their weight (normalised to deal with weight of all sizes)
                            width = (filtered_df['weight']-min(filtered_df['weight']))/(max(filtered_df['weight'])-min(filtered_df['weight']))*10,
                            font_weight= 'bold', 
                            edge_cmap = plt.cm.bone,
                             # Changing line colour according to weight
                            edge_color = filtered_df['weight'],
                            font_color = "#2A2925", 
                            font_size = 6,
                            node_color = "#E5C300",
                            node_size = 150)
        
        # Add colour bar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.bone, norm=plt.Normalize(vmin = min(filtered_df['weight']), vmax=max(filtered_df['weight'])))
        
        sm._A = []
    
        cbar = plt.colorbar(sm, shrink=0.6)

        cbar.set_label('Edge weight', rotation=270, labelpad=15)

        cbar.ax.tick_params(labelsize=6)

        # Save graph
        graph_path = Path.cwd()  / 'viz' / f"{self.identifier}_network_graph.png" 

        plt.savefig(graph_path, dpi=300, bbox_inches="tight")

        return graph


    # Defining function for creating and saving df containing degree, betweenness, and eigenvector centrality scores for all nodes in the network
    '''
    Generates a csv file containing three centrality measures for each node and saves it to output folders
    Args:
        graph : Networkx graph generated from 'get_network_graph'
        out_dir (Posix path) : Path for output
    '''
    def get_centrality_df(self, graph, out_dir):

        # Calculate metrics 
        degree = nx.degree_centrality(graph)

        betweenness = nx.betweenness_centrality(graph)

        eigenvector = nx.eigenvector_centrality(graph)

        # Creating dataframe
        centrality_df = pd.DataFrame({
            'nodes': list(degree.keys()),
            'degree': list(degree.values()),
            'betweenness': list(betweenness.values()),
            'eigenvector': list(eigenvector.values()),  
        })

        # Saving dataframe to output folder
        df_path = out_dir / f"{self.identifier}_centrality_df.csv"  

        centrality_df.to_csv(df_path) # Saving the df as a csv file


# Executing main function when script is run as main module (e.g. in command line)
if __name__ == '__main__':

    #Create an argument parser from argparse
    parser = argparse.ArgumentParser(description = "[INFO] Network Analysis of Entity Co-occurrences",
                                formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-tf', 
                        metavar="--text_file",
                        type=str,
                        help=
                        "[DESCRIPTION] The name of the input text file \n"
                        "[TYPE]        str \n"
                        "[EXAMPLE]     -tf true_news.csv \n",
                        required=False)


    parser.add_argument('-ef', 
                        metavar="--edge_file",
                        type=str,
                        help=
                        "[DESCRIPTION] The name of the input edge_file \n"
                        "[TYPE]        str \n"
                        "[EXAMPLE]     -fn edges_df.csv \n",
                        required=False)

    parser.add_argument('-id', 
                        metavar="--identifier",
                        type=str,
                        help=
                        "[DESCRIPTION] Prefix for output files to identify files \n"
                        "[TYPE]        str \n"
                        "[EXAMPLE]     -id true_news \n",
                        required=False)

    parser.add_argument('-ne',
                        metavar="--n_edges",
                        type=int,
                        help=
                        "[DESCRIPTION] The number of edges to keep in the network. \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     50 \n"
                        "[EXAMPLE]     -ne 50 \n",
                        required=False,           
                        default=50)

    parser.add_argument('-tg',
                        metavar="--tag",
                        type=str,
                        help=
                        "[DESCRIPTION] Which entities to extract (LOC, PERSON, ORG) \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     PERSON \n"
                        "[EXAMPLE]     -tg PERSON",
                        required=False,           
                        default='PERSON')

    main(parser.parse_args())