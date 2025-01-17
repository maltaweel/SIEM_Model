'''
SIEM Model

See Altaweel, M., Palmisano, A., Hritz, C., 2015. 
Evaluating Settlement Structures in the Ancient Near East using Spatial Interaction Entropy Maximization. 
Structure and Dynamics: eJournal of Anthropological and Related Sciences 8. 
https://doi.org/10.5070/SD981028281.


Created on Dec 18, 2024

@author: mark-altaweel
'''
import math
from geopy.distance import distance
import utm
from geopy.point import Point

class Settlement:
    alpha=0
    beta=0
    
    points={}
    settlements={}
    settlement_x={}
    settlement_y={}
    settlement_z={}
    population={}
    attractiveness={}
    distance={}
    flow={}
    linkFlow=dict()
    speed=0.00000001
    constant=1
    totalPopulation=100000
    
    def _init_(self):
        self.speed=0.00000001
        self.constant=1
    
        
    def clearAll(self):
        self.points.clear()
        self.settlements.clear()
        self.settlement_x.clear()
        self.settlement_y.clear()
        self.settlement_z.clear()
        self.population.clear()
        self.attractiveness.clear()
        self.distance.clear()
        self.flow.clear()
        self.linkFlow=dict()
    
    def calculateDistance(self,i,j):
       
  
        
        i_y=self.settlement_y[i]
        i_x=self.settlement_x[i]
        i_z=self.settlement_z[i]
                
      #  cord1=utm.to_latlon(i_x, i_y, 32, 'N')
      #  coords_1 = Point(i_x,i_y)
        
        
            
        j_y=self.settlement_y[j]
        j_x=self.settlement_x[j]
        j_z=self.settlement_z[j]
            
        key=str(i)+'-'+str(j)
     #   cord2=utm.to_latlon(j_x, j_y, 32, 'N')
     #   coords_2=Point(j_x,j_y)
            
    
      #  dist=distance(coords_1, coords_2).km 
            
        elev=math.fabs(i_z-j_z)
        
        dist1=math.sqrt(math.pow(i_x-j_x,2)+math.pow(i_y-j_y,2))
            
        dist=math.sqrt(dist1**2 + elev**2)*0.001
        
        if math.isnan(dist):
            dist=10000000.0
            
        self.distance[key]=dist
        
       
            
        
        return dist
            
    def setFlow(self):
        print('reset flow')
        
        for i in self.settlements:
            
            self.flow[i]=0.01
            
            
    def calculate_flow(self):
        
        sets=self.settlements
        
        for i in self.settlements:
            
            pop=self.population[i]
            totalAttract=self.totalAttractivenessDistance(i)
            
            for j in sets:
                if i==j:
                    continue
            
                attract=self.attractiveness[j]
                key=str(i)+'-'+str(j)
                if key in self.distance:
                    dist=self.distance[key]
                else:
                    dist=self.calculateDistance(i, j)
                parta=math.pow(attract,self.alpha)*math.pow(math.e,-self.beta*dist)
                
                fl=pop*(parta/totalAttract)
                
                existingFlow=self.flow[j]
                self.flow[j]=fl+existingFlow
                
                self.linkFlow[key]=parta
                
                
    
    def totalAttractivenessDistance(self,i):
        totalAttract=0.0

        for k in self.attractiveness.keys():
            if i==k:
                continue
            key=str(i)+'-'+str(k)
            
            if key in self.distance:
                    dist=self.distance[key]
            else:
                    dist=self.calculateDistance(i, k)
            attract=self.attractiveness[k]
            try:
                newattract=math.pow(attract,self.alpha)*math.pow(math.e,-self.beta*dist)
                totalAttract+=newattract
         
            except:
                print('error')
            
            
        return totalAttract
        
        
    def adjustAdvantages(self):
        
        for j in self.attractiveness.keys():
            
            attract=self.attractiveness[j]
            
            newAttract=attract+(self.speed*(self.flow[j]-(self.constant*attract)))
            
            self.attractiveness[j]=newAttract
    
    def totalAttract(self):
        totalAttract=0.0
        for i in self.population:
            totalAttract+=self.attractiveness[i]
        
        return totalAttract  
    
    def adjustPopulation(self):
        totalAttract=self.totalAttract()
        for i in self.population:
           
            attract=self.attractiveness[i]
            
            newPop=self.totalPopulation*(attract/totalAttract)
            print(str(attract)+':'+str(totalAttract)+':'+str(newPop))
            self.population[i]=int(newPop)
            

            
            '''
            populationNow=populationNow-self.population[i]
            if populationNow<0:
                self.population[i]=self.population[i]+populationNow
                populationNow=0
            '''   
            
            
            
            
                