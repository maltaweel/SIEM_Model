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
    
    def setFlow(self):
        print('reset flow')
        
        for i in self.settlements:
            
            self.flow[i]=0.01
            
            
    def calculate_flow(self):
        
        sets=self.settlements
        
        for i in self.settlements:
            
            pop=self.population[i]
            totalAttract=self.totalAttractiveness(i)
            
            for j in sets:
                if i==j:
                    continue
            
                attract=self.attractiveness[j]
                key=str(i)+'-'+str(j)
                dist=self.distance[key]
                parta=math.pow(attract,self.alpha)*math.pow(math.e,-self.beta*dist)
                
                fl=pop*(parta/totalAttract)
                
                existingFlow=self.flow[j]
                self.flow[j]=fl+existingFlow
                
                self.linkFlow[key]=parta
                
                
    
    def totalAttractiveness(self,i):
        totalAttract=0.0

        for k in self.attractiveness.keys():
            if i==k:
                continue
            key=str(i)+'-'+str(k)
            dist=self.distance[key]
            attract=self.attractiveness[k]
            attract=(math.pow(attract,self.alpha)*math.pow(math.e,-self.beta*dist))
            totalAttract+=attract
         
            
            
        return totalAttract
        
        
    def adjustAdvantages(self):
        
        for j in self.attractiveness.keys():
            
            attract=self.attractiveness[j]
            
            newAttract=attract+(self.speed*(self.flow[j]-(self.constant*attract)))
            
            self.attractiveness[j]=newAttract
            
    
    def adjustPopulation(self):
        
      # populationNow=self.totalPopulation
        for i in self.population:
            totalAttract=self.totalAttractiveness(i)
            attract=self.attractiveness[i]
            
            newPop=self.totalPopulation*(attract/totalAttract)
            self.population[i]=int(newPop)
            
            print(self.population[i])
            
            '''
            populationNow=populationNow-self.population[i]
            if populationNow<0:
                self.population[i]=self.population[i]+populationNow
                populationNow=0
            '''   
            
            
            
            
                