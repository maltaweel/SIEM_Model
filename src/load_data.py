'''
Created on Dec 18, 2024

@author: mark-altaweel
'''

import sys, os
import  geopandas as gpd
import geopy.distance
from settlement import Settlement
from html5lib.filters import alphabeticalattributes



def readData(file,alpha,beta):
    
    pn=os.path.abspath(__file__)
    pn=pn.split("src")[0]
    path=os.path.join(pn,'data',file)
    
    
    gdf = gpd.read_file(path)
    
    lat=gdf['LAT']
    lon=gdf['LON']
    elevation=gdf['Altitudine']
    
    s=Settlement()
    
    n=0
    for i in range(0,len(lat)):
        n+=1
        s.alpha=alpha
        s.beta=beta
        s.settlements.append(i)
        s.settlement_x[i]=lon[i]
        s.settlement_y[i]=lat[i]
        s.settlement_z[i]=elevation[i]
        s.population[i]=100
        s.attractiveness[i]=1.0
        s.flow[i]=1.0
    
        
        
    s.totalPopulation=n*s.population[0]  
    
    return s  
    
    
def calculateDistance(s):
       
    setts=s.settlements
       
    for i in s.settlements:

        i_y=s.settlement_y[i]
        i_x=s.settlement_x[i]
        i_z=s.settlement_z[i]
        
        coords_1 = (i_x,i_y,i_z)
        
        for j in setts:
                   
            if i==j:
                continue
            
            j_y=s.settlement_y[i]
            j_x=s.settlement_x[i]
            j_z=s.settlement_z[i]
            
            key=str(i)+'-'+str(j)
               
            coords_2=(j_x,j_y,j_z)
             
            dist=geopy.distance.geodesic(coords_1, coords_2).km 
            
            s.distance[key]=dist
               
        

#launch the main
if __name__ == "__main__":
    file = str(sys.argv[1])
    alpha=float(sys.argv[2])
    beta=float(sys.argv[3])
    
    s=readData(file,alpha,beta)
    calculateDistance(s)
    
    