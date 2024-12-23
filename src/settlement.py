'''
Created on Dec 18, 2024

@author: mark-altaweel
'''
import math

class Settlement:
    alpha=0
    beta=0
    
    points=[]
    settlements=[]
    settlement_x={}
    settlement_y={}
    settlement_z={}
    population={}
    attractiveness={}
    distance={}
    flow={}
    linkFlow=dict()
    speed=0.001
    constant=1
    totalPopulation=100000
    
    def setFlow(self):
        print('reset flow')
        
        for i in self.settlements:
            
            self.flow[i]=1.0
            
            
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
                
                if totalAttract==0.0:
                    print('stop')
                fl=pop*(parta/totalAttract)
                
                existingFlow=self.flow[j]
                self.flow[j]=existingFlow+fl
                
                self.linkFlow[key]=parta
                
    
    def totalAttractiveness(self,i):
        totalAttract=0.0

        for k in self.attractiveness.keys():
            if i==k:
                continue
            key=str(i)+'-'+str(k)
            dist=self.distance[key]
            attract=self.attractiveness[k]
            attract=(math.pow(attract,self.alpha)*math.pow(math.e,-self.beta*dist))*0.0000000000000000001
            totalAttract+=attract+totalAttract
            print(totalAttract)
            
        
        return totalAttract
        
        
    def adjustAdvantages(self):
        
        for j in self.attractiveness.keys():
            
            attract=self.attractiveness[j]
            
            newAttract=attract+(self.speed*(self.flow[j]-(self.constant*attract)))
            
            self.attractiveness[j]=newAttract
            
    
    def adjustPopulation(self):
         
        for i in self.population:
            totalAttract=self.totalAttractiveness(i)
            attract=self.attractiveness[i]
            
            newPop=self.totalPopulation*(attract/totalAttract)
            self.population[i]=int(newPop)
            
            
            
            
                