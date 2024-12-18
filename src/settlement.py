'''
Created on Dec 18, 2024

@author: mark-altaweel
'''
import math

class Settlement:
    alpha=0
    beta=0
    
    settlements=[]
    settlement_x={}
    settlement_y={}
    settlement_z={}
    population={}
    attractiveness={}
    distance={}
    flow={}
    speed=0.1
    constant=1
    totalPopulation=100000
    
    def setFlow(self):
        for i in self.settlements:
            
            self.flow[i]=0.0
            
            
    def calculate_flow(self):
        
        sets=self.settlements
        
        for i in self.settlements:
            
            pop=self.population[i]
            
            for j in sets:
                if i==j:
                    continue
            
                attract=self.attractiveness[j]
                key=str(i)+'-'+str(j)
                dist=self.distance[key]
                parta=math.pow(attract,self.alpha)*math.pow(math.e,-self.beta*dist)
                
                fl=pop*(parta/self.totalAttractiveness())
                
                existingFlow=self.flow[j]
                self.flow[j]=existingFlow+fl
                
  
    def adjustAttractiveness(self):
        
        for j in self.attractiveness.keys():
            
            attract=self.attractiveness[j]
            
            newAttract=attract+(self.speed*(self.flow[j]-(self.constant*attract)))
            
            self.attractiveness[j]=newAttract
            
    def totalAttractiveness(self):
        totalAttract=0.0
        for i in self.attractiveness.keys():
            attract=self.attractiveness[i]
            totalAttract=attract+totalAttract
            
        
        return totalAttract
        
    def adjustPopulation(self):
        
        totalAttract=self.totalAttractiveness()
        
        for i in self.population:
            
            attract=self.attractiveness[i]
            
            newPop=self.totalPopulation*(attract/totalAttract)
            self.population[i]=int(newPop)
            
            
            
            
                