'''
Created on Jan 6, 2025

@author: mark-altaweel
'''
from markov_clustering import run_mcl
from markov_clustering import get_clusters
import networkx as nx
import random
import settlement

G = nx.Graph()

class Graph:
    
    def createGraph(self,s):
        
        kL=s.linkFlow.keys()
        
        for li in kL:
            n1=int(li.split('-')[0])
            n2=int(li.split('-')[1])
            
            fl=s.linkFlow[li]
            dist=s.distance[li]
             
            sN1=s.settlements[n1]
            sN2=s.settlements[n2]
            
            G.add_node(sN1)
            G.add_node(sN2)
            
            G.add_edge(sN1,sN2,weight=fl,length=dist)
    
    def createMarkovCluster(self):  
        matrix = nx.to_scipy_sparse_matrix(G)
        result = run_mcl(matrix)           # run MCL with default parameters
        clusters = get_clusters(result)    # get clusters
        
        return clusters