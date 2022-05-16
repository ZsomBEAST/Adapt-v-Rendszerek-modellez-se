# -*- coding: utf-8 -*-
"""
Created on Wed May 11 20:45:58 2022

@author: Zsombesz
"""
import csv
import os
from random import random
import numpy as np



n = 0
individual=0
state = 0 #0->1->2->3->1->2->3
generation = 0
max_map_cnt=7
map_cnt=0

def roulette_wheel_selection(fitnesses):
    fit_sum = float(sum(fitnesses))
    chromosome_probabilities = fitnesses/fit_sum
    return np.sort(np.random.choice(10,10,p=chromosome_probabilities), axis=None)


def evolution(w, fitness, alpha = 0.2, chance = 0.05):
    global n, individual, state, generation, max_map_cnt, map_cnt, maps
    
    n_max=14
    r=w
    
    #az eredmény beírjuk a fileba
    result_csv = open("result.csv",'a')
    output = [str(w[0]),str(w[1]),str(w[2]),str(w[3]),str(w[4]),str(w[5]),str(w[6]),str(w[7]),str(w[8]),str(fitness)]
    result_csv.write(','.join(output))
    result_csv.write('\n')
    result_csv.close()
    
    n+=1
    
    if n >= n_max: #ha egy egyeden 10 szer végigmentünk
        avr=0.0
        params=[]
        with open("result.csv", newline='\n') as file:
            one_ind=csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
            for row in one_ind: # beleírjuk a resultsba
                avr += float(row[9]) #kiszámoljuk a fitnesek átlagát
                params=row
        avr /= n_max
        
        if state==0:
            s="population.csv"
            if individual >= 9:
                state=1
            r = [10*random(), 10*random(), 10*random(), 10*random(), 10*random(), 10*random(), 10*random(), 10*random(), 10*random()]
            #A 0. generációban az egyedek random számok 0-10 között
        elif state==2:
            s="childs.csv" #a childs-ba írjuk az eredményeket fitnessel
            #kiolvassuk a következő sulyokat a játék futtatásához
            r=[]
            with open("childs_tmp.csv", newline='\n') as file:
                child=csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
                for i,row in enumerate(child):
                    if i==individual:
                        for j in row:
                            r.append(j)
            if individual >= 9:
                state=3
            
        population = open(s,'a') #átlagostúl belekerül a populationbe az egyed
        output = [str(params[0]),str(params[1]),str(params[2]),str(params[3]),str(params[4]),str(params[5]),str(params[6]),str(params[7]),str(params[8]),str(avr)]
        population.write(','.join(output))
        population.write('\n')
        
        population.close() 
        file.close()
        os.remove("result.csv"); #új egyed jön, ezért töröljük a result -ot
        
        individual += 1 #jöhet a következő egyed
        n=0
    
    if individual >= 10:
        
        if state==3: #ha az utódok fitnese megvan és a legjobb 10 et keressük a 20 ból
            
            #szülők kiolvasás a populationból
            par_pop_fit=[]
            par_pop=np.zeros((10,9))
            
            #CSV file tömbbe rendezése
            with open("population.csv", newline='\n') as file:
                parents=csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
                for i,row in enumerate(parents): # kiolavssuk az összes egyed fitneszét
                    par_pop_fit.append(row[9]) #tömbe rendezzük őket a ruletthez
                    for j,value in enumerate(row): #az egyedeket is tömbbe rendezzük
                        if j <= 8 and i <= 9:
                            par_pop[i,j] = float(value)
           
            file.close()
            par_pop_fit=np.array(par_pop_fit)
            
            
            #utódok kiolvasás a childsból
            child_pop_fit=[]
            child_pop=np.zeros((10,9))
            
            #CSV file tömbbe rendezése
            with open("childs.csv", newline='\n') as file:
                childs=csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
                for i,row in enumerate(childs): # kiolavssuk az összes egyed fitneszét
                    child_pop_fit.append(row[9]) #tömbe rendezzük őket a ruletthez
                    for j,value in enumerate(row): #az egyedeket is tömbbe rendezzük
                        if j <= 8 and i <= 9:
                            child_pop[i,j] = float(value)
           
            file.close()
            child_pop_fit=np.array(child_pop_fit)
            
            #legjobb 10 kiválasztása fitnesz alapján
            big_pop = np.zeros((20,9))
            big_pop[0:10,:]=par_pop
            big_pop[10:20,:]=child_pop
            big_pop_fit = np.hstack((par_pop_fit,child_pop_fit))
            
            bests = np.argpartition(big_pop_fit, -10)[-10:]
            next_gen = np.zeros((10,9))
            next_gen_fit=np.zeros(10)
     
            avg=0.0
            for i in range(10):
                next_gen[i,:] = big_pop[int(bests[i]),:]
                next_gen_fit[i]=big_pop_fit[int(bests[i])]
                avg += big_pop_fit[int(bests[i])]
            
            avg /= 10
            generation += 1
            
            #elmentjük a generáció átlagos fitness értékét
            avarage_fit_csv = open("avr_fit.csv",'a') 
            avarage_fit_csv.write(str(generation))
            avarage_fit_csv.write(',')
            avarage_fit_csv.write(str(avg))
            avarage_fit_csv.write('\n')
            avarage_fit_csv.close() 
            
            #kimentjük az evolúció eredményét
            os.remove("population.csv")
            next_gen_csv = open("population.csv",'w') 
            s=""
            for i,row in enumerate(next_gen):
                for element in row:
                    s += str(element)
                    s += ','
                s += str(next_gen_fit[i])
                s += '\n'
            next_gen_csv.write(s)
            next_gen_csv.close()
            state=1 #egyből végezhetjük is a következő rulett kerék szelekciót
            print("Generáció:",generation," átlag méret:", avg)
            
        if state==1: #ha az utódokat határoztuk meg
                 
            par_pop_fit=[]
            par_pop=np.zeros((10,9))
            
            #CSV file tömbbe rendezése
            with open("population.csv", newline='\n') as file:
                population=csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
                for i,row in enumerate(population): # kiolavssuk az összes egyed fitneszét
                    par_pop_fit.append(row[9]) #tömbe rendezzük őket a ruletthez
                    for j,value in enumerate(row): #az egyedeket is tömbbe rendezzük
                        if j <= 8 and i <= 9:
                            par_pop[i,j] = float(value)
           
            file.close()
            par_pop_fit=np.array(par_pop_fit)
            
            #Szelekció
            survived_pop=np.zeros((10,9))
            
            selected = roulette_wheel_selection(par_pop_fit)
            
            for i in range(10):
                survived_pop[i,:] = par_pop[int(selected[i]),:]
            
            #Keresztezés
            child_pop=np.zeros((10,9))
            for i in range(5): #az összes súlyra ugyan úgy hat a keresztezés
                child_pop[i,:]   = alpha * survived_pop[i,:]   + (1-alpha) * survived_pop[9-i,:]
                child_pop[9-i,:] = alpha * survived_pop[9-i,:] + (1-alpha) * survived_pop[i,:]
            
            #Mutáció
            for i in range(10):
                for j in range(9):
                    mutation = random()
                    if mutation < chance:
                        multiplyer = 10 * random()**3 #egy 0 és egy 10 közötti számmal szorzunk
                        child_pop[i,j] *= multiplyer
             
            childs_csv = open("childs_tmp.csv",'w') #kimentjük az evolúció eredményét
            s=""
            for row in child_pop:
                for i,element in enumerate(row):
                    s += str(element)
                    if i<8:
                        s += ','
                s += '\n'
        
            childs_csv.write(s)
            childs_csv.close()
            
            try:
                os.remove("childs.csv")
            except:
                print("")
                
            state=2
                  
        individual=0
        
    map_cnt+=1
    if map_cnt >= max_map_cnt:
        map_cnt=0
    
    r.append(map_cnt)
    
    return r
            
  
        
            
        
    
    