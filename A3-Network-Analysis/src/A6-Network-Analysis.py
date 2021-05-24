# Importing packages
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


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

# Defining main function 
def main(args):

    # Adding arguments that can be specified in command line
    text_file = args.tf

    edge_file = args.ef

    n_edges = args.ne 

    tag = args.tg

    NetworkAnalysis(n_edges=n_edges, tag=tag, text_file=text_file, edge_file=edge_file)  # Calling main class 

# Setting class 'CountFunctions'
class NetworkAnalysis:

    def __init__(self,  n_edges, tag, text_file=None, edge_file=None):

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

        # If both text_file and edge_file args are none, set edge_file to example file provided in folder
        if text_file is None and edge_file is None:

            self.edge_file = "edges_df.csv"

        # If text file is given then generate and edge file 
        if text_file is not None: 
            
            # Generate edge file 
            generated_edge_file = self.get_edge_file(text_file=self.text_file, tag=self.tag, out_dir=out_dir)

            # Creating network graph using pre-defined graphing function
            graph = self.get_network_graph(edgefile=generated_edge_file, n_edges=self.n_edges, out_di =out_dir)

            # Calculating nodes metrics and saving df
            self.get_centrality_df(graph, out_dir=out_dir)

        # If text file is none, use edge_file passed in command line (or default if none)
        else:

            df = pd.read_csv(data_dir / f'{self.edgefile}')  # Read csv edgefile

            # Creating network graph using pre-defined graphing function
            graph = self.get_network_graph(edgefile=df, n_edges=self.n_edges, out_dir=out_dir)

            # Calculating nodes metrics and saving df
            self.get_centrality_df(graph, out_dir=out_dir)


    # Defining function for setting directory for the raw data
    def setting_data_directory(self):

        root_dir = Path.cwd()  # Setting root directory

        data_dir = root_dir / 'src' / 'data'   # Setting data directory

        return data_dir


    # Defining function for setting directory for the output
    def setting_output_directory(self):

        root_dir = Path.cwd()  # Setting root directory

        out_dir = root_dir / 'src' / 'output' # Setting output directory

        return out_dir
    
    # Defining function for generating edge file of all edges between nodes and a weight column
    '''
    Generates a network graph from an edge file containing a specified number of edges
    Args:
        edge_file (pd datatframe): Edge file in a pd data frame format containing the following columns: 'nodeA', 'nodeB', 'weight
        n_edges (integer): Number of edges to keep 
        out_dir (Posix path) : Path for output
    Returns:
        graph: Final network graph

    '''
    def get_edge_file(self, text_file, tag, out_dir):



    # Defining function for generating plot of network
    '''
    Generates a network graph from an edge file containing a specified number of edges
    Args:
        edge_file (pd datatframe): Edge file in a pd data frame format containing the following columns: 'nodeA', 'nodeB', 'weight
        n_edges (integer): Number of edges to keep 
        out_dir (Posix path) : Path for output
    Returns:
        graph: Final network graph

    '''
    def get_network_graph(self, edge_file, n_edges, out_dir):
        
        # Selecting only the desired number of edges with the highest weight scores 
        filtered_df = edge_file.sort_values('weight', ascending = False).head(n_edges) # Contrary to setting a min_edge_weight, this method can be applied to all datasets 
        
        # Deleting extra column generated by previous line 
        del filtered_df["Unnamed: 0"]

        # Generating network graph
        graph = nx.from_pandas_edgelist(filtered_df, 'nodeA', 'nodeB', ["weight"])        
    
        pos = nx.draw_shell(graph,
                            with_labels = True, 
                            width = filtered_df['weight']/2500, # Weighting the width of the edges by their weight
                            font_weight= 'bold', 
                            edge_cmap = plt.cm.hsv,
                            edge_color = filtered_df['weight'], # Changing line colour according to weight - unfortunately I couldn't add a colorbar but it still looks kinda cool
                            font_color = "#2A2925", 
                            font_size = 6,
                            node_color = "#BD7575",
                            node_size = 150)
                            # Needs title

        # Save graph
        graph_path = out_dir / "network.png" 

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
        df_path = out_dir / "centrality_df.csv"  

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
                        "[EXAMPLE]     -fn edges_df.csv",
                        required=False)


    parser.add_argument('-ef', 
                        metavar="--edge_file",
                        type=str,
                        help=
                        "[DESCRIPTION] The name of the input edge_file \n"
                        "[TYPE]        str \n"
                        "[EXAMPLE]     -fn edges_df.csv",
                        required=False)

    parser.add_argument('-ne',
                        metavar="--n_edges",
                        type=int,
                        help=
                        "[DESCRIPTION] The number of edges to keep in the network. \n"
                        "[TYPE]        int \n"
                        "[DEFAULT]     50 \n"
                        "[EXAMPLE]     -ne 50",
                        required=False,           
                        default=50)

    parser.add_argument('-tg',
                        metavar="--tag",
                        type=str,
                        help=
                        "[DESCRIPTION] The tag which identifies which entities should be extract (e.g. LOC, PERSON, ORG \n"
                        "[TYPE]        str \n"
                        "[DEFAULT]     PERSON \n"
                        "[EXAMPLE]     -tg PERSON",
                        required=False,           
                        default='PERSON')

    main(parser.parse_args())