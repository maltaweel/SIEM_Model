'''
Data loader and output for SIEM model.

Created on Dec 18, 2024

@author: mark-altaweel
'''

import sys, os, math, random
import utm
from geopy.distance import distance
from geopy.point import Point
from fiona.crs import from_epsg
import  geopandas as gpd
from settlement import Settlement
from html5lib.filters import alphabeticalattributes
from shapely.geometry import mapping, Polygon
import fiona
from markov_graph import Graph

from_epsg(25832)

pn=os.path.abspath(__file__)
pn=pn.split("src")[0]

totalLinkFlow={}
totalDistance={}
totalSettlement=[]
totalFlow={}
totalAttractiveness={}
totalLocations={}
totalPopulation={}
locations={}

def randomBootstrap(n):
    a = random.randint(0,100)
    
    if n > a:
        return True
    else:
        return False
    

def tallyResults(s):
    
    settsOther=s.settlements
    for i in s.settlements:
        p1=s.points[i]
        totalLocations[i]=(p1.x,p1.y)
            
        for j in settsOther:
            if i==j:
                continue
      
            key=str(i)+'-'+str(j)
            
            
            
            fl=s.linkFlow[key]
            pop=s.population[i]
            flo=s.flow[i]
            atract=s.attractiveness[i]
            
            if i not in totalDistance:
                totalDistance[key]=s.distance[key]
                
            if key in totalLinkFlow:
                fl+=totalLinkFlow[key]
                
            if i in totalFlow:
                flo+=totalFlow[i]
            
            if i in totalAttractiveness:
                atract+=totalAttractiveness[i]
                
            if i in totalPopulation:
                pop+=totalPopulation[i]
            
            if i not in totalSettlement:
                totalSettlement.append(i)
                
            if i not in locations:
                locations[i]=p1
            
            totalLinkFlow[key]=fl 
            totalPopulation[i]=pop 
            totalFlow[i]=flo
            totalAttractiveness[i]=atract          
    
    
def readData(file,alpha,beta,randomN):
    

    path=os.path.join(pn,'data',file)
    
    
    gdf = gpd.read_file(path)
    
    lat=gdf['LAT']
    lon=gdf['LON']
    p=gdf['geometry']
    elevation=gdf['Z1']
    
    s=Settlement()
    
    numbers=[]
    for i in range(0,len(lat)):
        if randomBootstrap(randomN) is False:
            continue
        else:
            numbers.append(i)
    
    n=0
    for i in numbers:
        n+=1
        s.alpha=alpha
        s.beta=beta
        s.points[i]=p[i]
        s.settlements[i]=i
        s.settlement_x[i]=lon[i]
        s.settlement_y[i]=lat[i]
        s.settlement_z[i]=elevation[i]
        s.population[i]=100
        s.attractiveness[i]=1.0
        s.flow[i]=1.0
    
        
        
    s.totalPopulation=n*100  
    
    return s  

def outputResults(numberofRuns):
    
    # Define a point feature geometry with one attribute
    schema = {
    'geometry': 'Point',
    'properties': {'id': 'int', 'flow':'float','attractiveness':'float','population':'float'},
    }
    
    schema2 = {
    'geometry':'LineString',
    'properties':[('id','str'),('flow','float')]
    }
    
   
    path=os.path.join(pn,'output','point_output')
    
    
    path2=os.path.join(pn,'output','line')
    
    with fiona.open(path, 'w', 'ESRI Shapefile',schema) as c:
        
        for i in totalSettlement:
            c.write({
                'geometry': mapping(locations[i]),
                'properties': {'id': i,'flow':float(totalFlow[i]/numberofRuns),
                               'attractiveness':float(totalAttractiveness[i]/numberofRuns),
                               'population':int(totalPopulation[i]/numberofRuns)},
                })
            
            
        
        c.close()   
            
    
    with fiona.open(path2, 'w', 'ESRI Shapefile',schema2) as c2:        #open a fiona object
        
            settsOther=totalSettlement
            for i in totalSettlement:
            
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
            
    
    
def calculateDistance(s):
       
    setts=s.settlements
       
    for i in s.settlements:

        i_y=s.settlement_y[i]
        i_x=s.settlement_x[i]
        i_z=s.settlement_z[i]
                
        cord1=utm.to_latlon(i_x, i_y, 32, 'N')
        coords_1 = Point(cord1[0],cord1[1])
        
        for j in setts:
                  
            if i==j:
                continue
            
            j_y=s.settlement_y[j]
            j_x=s.settlement_x[j]
            j_z=s.settlement_z[j]
            
            key=str(i)+'-'+str(j)
            cord2=utm.to_latlon(j_x, j_y, 32, 'N')
            coords_2=Point(cord2[0],cord2[1])
            
    
            dist=distance(coords_1, coords_2).km 
            
            elev=math.fabs(i_z-j_z)
            
            dist=math.sqrt(dist**2 + elev**2)
            
            s.distance[key]=dist
               
        

#launch the main
if __name__ == "__main__":
    file = str(sys.argv[1])  #shapefile settlement data
    alpha=float(sys.argv[2]) #alpha value
    beta=float(sys.argv[3])  #beta value
    iterations=float(sys.argv[4]) #number of iterations
    randomN=int(sys.argv[5]) #random number of settlements (percentage) to select
    numberofRuns=int(sys.argv[6]) #number of total runs
    
    
    for nn in range(0,numberofRuns):
        s=readData(file,alpha,beta,randomN)
        calculateDistance(s)
        s.setFlow()
        
    
        for i in range(0,int(iterations)):
            s.calculate_flow()
            s.adjustAdvantages()
            s.adjustPopulation()
    
        tallyResults(s)
        
    
 #  g=Graph()
 #  g.createGraph(totalSettlement,totalLinkFlow,totalDistance,totalLocations)
 #  clusters=g.createMarkovCluster(totalLocations)
 #  g.outputResults(totalSettlement, locations, totalLinkFlow, totalFlow, numberofRuns, clusters)
    
    outputResults(numberofRuns)
    
    
    