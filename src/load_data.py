'''
Data loader and output for SIEM model.

Created on Dec 18, 2024

@author: mark-altaweel
'''
from copy import copy
import sys, os, math, random, csv
from fiona.crs import from_epsg
import  geopandas as gpd
from settlement import Settlement
from html5lib.filters import alphabeticalattributes
from shapely.geometry import mapping, Polygon
import fiona
from markov_graph import Graph
import gc
from azure.mgmt.purview.models._models_py3 import AccountEndpoints,\
    AccountPropertiesEndpoints
from sympy.core import alphabets

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
set_ment=None

def randomBootstrap(n):
    a = random.randint(0,100)
    
    if n > a:
        return True
    else:
        return False

def writeOutput(s,rn):
    
    pathway=os.path.join(pn,'output','csv_output','output_'+str(rn)+'.csv')
    
    fieldnames = ['Settlement','LinkedSettlement','LinkFlow','TotalDistance','Flow','Attractiveness','Location','Population']
    #print results out
    try:
        with open(pathway, 'w') as csvf:
             
            writer = csv.DictWriter(csvf, fieldnames=fieldnames)

            writer.writeheader()
            
            for i in totalSettlement:
                
                atract=totalAttractiveness[i]
                pop=totalPopulation[i]
                p1=locations[i]
                flow=totalFlow[i]
                
                hasKey=False
                for k in totalLinkFlow.keys():
                    f=int(k.split('-')[1])
                    
                    
                    if i == f:
                        hasKey=True
                        kp=int(k.split('-')[0])
                        fl=totalLinkFlow[k]
                        td=totalDistance[k]
    
                        writer.writerow({'Settlement': str(i),'LinkedSettlement':str(kp),'LinkFlow':str(fl),
                            'TotalDistance':str(td),'Flow':str(flow),'Attractiveness':str(atract),
                            'Location':str(str(p1.x)+' '+str(p1.y)),'Population':str(pop)})
                        
                    
                if hasKey==False:
                    writer.writerow({'Settlement': str(i),'LinkedSettlement':'NA','LinkFlow':'NA',
                            'TotalDistance':'NA','Flow':str(flow),'Attractiveness':str(atract),
                            'Location':str(str(p1.x)+' '+str(p1.y)),'Population':str(pop)})   
            
            totalAttractiveness.clear()
            totalDistance.clear()
            totalFlow.clear()
            totalLinkFlow.clear()
            totalLocations.clear()
            totalPopulation.clear()
            totalSettlement.clear()
            locations.clear()
  
    
    except IOError:
        print ("Could not read file:", IOError)
        
        

def tallyResults(s):
    
    settsOther=s.settlements
    for i in s.settlements:
        p1=s.points[i]
        try:
            totalLocations[i]=(p1.x,p1.y)
        except:
            continue
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
    
    ss=Settlement()
    
    
    n=0
    for i in range(0,len(lat)):
        n+=1
        ss.alpha=alpha
        ss.beta=beta
        ss.points[i]=p[i]
        ss.settlements[i]=i
        ss.settlement_x[i]=lon[i]
        ss.settlement_y[i]=lat[i]
        ss.settlement_z[i]=elevation[i]
        ss.population[i]=100
        ss.attractiveness[i]=1.0
        ss.flow[i]=1.0
    
        
        
    ss.totalPopulation=n*100  
    gc.collect()
    return ss

def selectRandom(settlement):

    i=0
    points={}
    settlement_x={}
    settlement_y={}
    settlement_z={}
    population={}
    attractiveness={}
    flow={}
    settlements={}
    for s in settlement.settlements.keys():
        
        if randomBootstrap(randomN) is False:
            continue
        else:
            
            points[i]=settlement.points[s]
            settlements[i]=s
            settlement_x[i]=settlement.settlement_x[s]
            settlement_y[i]=settlement.settlement_y[s]
            settlement_z[i]=settlement.settlement_z[s]
            population[i]=100
            attractiveness[i]=1.0
            flow[i]=1.0
            i+=1
            
    sNew=Settlement()
    sNew.points=points  
    sNew.settlements=settlements
    sNew.settlement_x=settlement_x
    sNew.settlement_y=settlement_y
    sNew.settlement_z=settlement_z
    sNew.population=population
    sNew.attractiveness=attractiveness
    sNew.flow=flow
    
    return sNew

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
            
    
    

               
        

#launch the main
if __name__ == "__main__":
    file = str(sys.argv[1])  #shapefile settlement data
    alpha=float(sys.argv[2]) #alpha value
    beta=float(sys.argv[3])  #beta value
    iterations=float(sys.argv[4]) #number of iterations
    randomN=int(sys.argv[5]) #random number of settlements (percentage) to select
    numberofRuns=int(sys.argv[6]) #number of total runs
    
    totalS=readData(file,alpha,beta,randomN)
    set_ment=totalS
    
    print(len(totalS.settlements))
    for nn in range(0,numberofRuns):
        sett=selectRandom(totalS)
        sett.alpha=alpha
        sett.beta=beta
        print(len(sett.settlements))
        sett.setFlow()
        
    
        for i in range(0,int(iterations)):
            sett.calculate_flow()
            sett.adjustAdvantages()
            sett.adjustPopulation()
    
        tallyResults(sett)
        print('Run Number: '+str(nn))
#       writeOutput(sett,nn)
#       gc.collect()

    
 #  g=Graph()
 #  g.createGraph(totalSettlement,totalLinkFlow,totalDistance,totalLocations)
 #  clusters=g.createMarkovCluster(totalLocations)
 #  g.outputResults(totalSettlement, locations, totalLinkFlow, totalFlow, numberofRuns, clusters)
    
    outputResults(numberofRuns)
    
    
    