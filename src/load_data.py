'''
Created on Dec 18, 2024

@author: mark-altaweel
'''

import sys, os, math
import utm
from geopy.distance import distance
from geopy.point import Point
from fiona.crs import from_epsg
import  geopandas as gpd
from settlement import Settlement
from html5lib.filters import alphabeticalattributes
from shapely.geometry import mapping, Polygon
import fiona

from_epsg(25832)

pn=os.path.abspath(__file__)
pn=pn.split("src")[0]
    
def readData(file,alpha,beta):
    

    path=os.path.join(pn,'data',file)
    
    
    gdf = gpd.read_file(path)
    
    lat=gdf['LAT']
    lon=gdf['LON']
    p=gdf['geometry']
    elevation=gdf['Z1']
    
    s=Settlement()
    
    n=0
    for i in range(0,len(lat)):
        n+=1
        s.alpha=alpha
        s.beta=beta
        s.points.append(p[i])
        s.settlements.append(i)
        s.settlement_x[i]=lon[i]
        s.settlement_y[i]=lat[i]
        s.settlement_z[i]=elevation[i]
        s.population[i]=100
        s.attractiveness[i]=1.0
        s.flow[i]=1.0
    
        
        
    s.totalPopulation=n*s.population[0]  
    
    return s  

def outputResults(s):
    
    # Define a point feature geometry with one attribute
    schema = {
    'geometry': 'Point',
    'properties': {'id': 'int', 'flow':'float','attractiveness':'float','population':'float'},
    }
    
    schema2 = {
    'geometry':'LineString',
    'properties':[('id','str'),('flow','float')]
    }
    
   
    

    path=os.path.join(pn,'output','output.shp')
    
    path2=os.path.join(pn,'output','line')
    
    with fiona.open(path, 'w', 'ESRI Shapefile',schema) as c:
        
        for i in s.settlements:
            c.write({
                'geometry': mapping(s.points[i]),
                'properties': {'id': s.settlements[i],'flow':s.flow[i],'attractiveness':s.attractiveness[i],
                               'population':s.population[i]},
                })
            
            
        
        c.close()   
            
    
    with fiona.open(path2, 'w', 'ESRI Shapefile',schema2) as c2:        #open a fiona object
        
            settsOther=s.settlements
            for i in s.settlements:
            
                for j in settsOther:
                    if i==j:
                        continue
                
                    p1=s.points[i]
                    p2=s.points[j]
                
                    xyList=[(p1.x,p1.y),(p2.x,p2.y)]
                
                    key=str(i)+'-'+str(j)
                
                    fl=s.linkFlow[key]
                
                    c2.write({
                        'geometry': {'type':'LineString',
                                     'coordinates': xyList},
                        'properties': {'id': key,'flow':fl},
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
    file = str(sys.argv[1])
    alpha=float(sys.argv[2])
    beta=float(sys.argv[3])
    iterations=float(sys.argv[4])
    
    s=readData(file,alpha,beta)
    calculateDistance(s)
    
    for i in range(0,int(iterations)):
        s.setFlow()
        s.calculate_flow()
        s.adjustAdvantages()
        s.adjustPopulation()
    
    outputResults(s)
    
    