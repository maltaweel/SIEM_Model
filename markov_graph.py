'''
Created on Jan 6, 2025

@author: mark-altaweel
'''
import os
from markov_clustering import run_mcl
import markov_clustering as mcl
from markov_clustering import get_clusters
import networkx as nx

import random
import settlement

import fiona
from fiona.crs import from_epsg

G = nx.Graph()

from_epsg(25832)

pn=os.path.abspath(__file__)
pn=pn.split("src")[0]


class Graph:
    
    def createGraph(self,totalSettlement,totalLinkFlow,totalDistance,totalLocations):
        
        kL=totalLinkFlow.keys()
        
        for i in range(0,len(totalSettlement)):
            G.add_node(i)
        
        for li in kL:
            n1=int(li.split('-')[0])
            n2=int(li.split('-')[1])
            
            fl=totalLinkFlow[li]
            dist=totalDistance[li]
                      
            G.add_edge(n1,n2,weight=fl,length=dist)
            G.add_node(n1)
            G.add_node(n2)
    
    def createMarkovCluster(self,positions):  
        matrix = nx.to_scipy_sparse_matrix(G)
        result = run_mcl(matrix, inflation=1.4)           # run MCL with default parameters
        clusters = get_clusters(result)    # get clusters
        positions=nx.spring_layout(G)
        mcl.draw_graph(matrix, clusters, pos=positions, node_size=50, with_labels=False, edge_color="silver")

        
        return result
    
   
    def outputResults(self,totalSettlement,locations,totalLinkFlow,totalFlow,numberofRuns,clusters):
                
        path2=os.path.join(pn,'output','markov_cluster')
        
        schema2 = {
              'geometry':'LineString',
            'properties':[('id','str'),('flow','float')]
            }
          
        with fiona.open(path2, 'w', 'ESRI Shapefile',schema2) as c2:        #open a fiona object
        
            settsOther=totalSettlement
            t=clusters.T
            for i in clusters:
            
                largestFlow=0.0
                keepKey=''
                keepXY=[]
                for j in settsOther:
                    if i==j:
                        continue
                
                    p1=locations[i]
                    p2=locations[j]
                
                    xyList=[(p1.x,p1.y),(p2.x,p2.y)]
                
                    key=str(i)+'-'+str(j)
                
                    fl=totalLinkFlow[key]
                    if (fl>largestFlow) and (totalFlow[j]>totalFlow[i]):
                        keepKey=key
                        keepXY=xyList
                        largestFlow=fl
                
                if largestFlow>0.0:
                    c2.write({
                        'geometry': {'type':'LineString',
                                     'coordinates': keepXY},
                                     'properties': {'id': keepKey,'flow':float(largestFlow/numberofRuns)},
                        })
                
            c2.close()
          