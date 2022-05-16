# -*- coding: utf-8 -*-
"""
Created on Thu May  5 15:13:35 2022

@author: Zsombesz
"""

#encoding: utf-8

import time
from Client import SocketClient
import json
import numpy as np
import Evolution
from random import seed
import os

# NaiveHunter stratégia implementációja távoli eléréshez.
class RemoteNaiveHunterStrategy:

    def __init__(self):
        try:
            os.remove("childs_tmp.csv")
            os.remove("childs.csv")
            os.remove("avr_fit.csv")
            os.remove("population.csv")
        except:
            print("")
        # Dinamikus viselkedéshez szükséges változók definíciója
        self.direction_prev=8
        self.oldpos = None
        self.oldcounter = 0
        self.constdir=np.random.randint(0, 7, 1)
        
        
        self.maps=["03_blockade.txt","04_mirror.txt","05_own.txt","06_own.txt","07_own.txt","map_L.txt","map_x.txt"]
        self.map_cnt = 0
        
        #tanitandó súlyok
        self.w_dist=0.853722288130363
        self.w_stay=0.301232916143439
        self.w_wall = 0.187202686619754
        self.w_neighbor1 = 0.0783018154839022
        self.w_neighbor2 = 0.0218596344466767
        self.w_chase = 3.99504942390201
        self.w_escape = 0.987853940238873
        self.w_stuck = 1.0
        self.w_tomiddle=0.00230515773821561
        #look up table
        self.cord_inf =np.array([[5,6,5],
                                [108,7,4],
                                [107,7,4],
                                [106,6,4],
                                [105,6,4],
                                [104,6,4],
                                [103,5,4],
                                [102,5,4],
                                [209,7,4],
                                [208,7,3],
                                [207,7,3],
                                [206,6,3],
                                [205,6,3],
                                [204,6,3],
                                [203,5,3],
                                [202,5,3],
                                [201,5,4],
                                [309,7,4],
                                [308,7,3],
                                [307,7,2],
                                [306,7,2],
                                [305,6,2],
                                [304,6,2],
                                [303,5,2],
                                [302,5,3],
                                [301,5,4],
                                [409,0,4],
                                [408,0,3],
                                [407,0,2],
                                [406,7,1],
                                [405,6,1],
                                [404,5,1],
                                [403,5,2],
                                [402,4,3],
                                [401,4,4],
                                [510,0,5],
                                [509,0,4],
                                [508,0,3],
                                [507,0,2],
                                [506,0,1],
                                [505,8,0],
                                [504,4,1],
                                [503,4,2],
                                [502,4,3],
                                [501,4,4],
                                [500,4,5],
                                [609,0,4],
                                [608,0,3],
                                [607,1,2],
                                [606,1,1],
                                [605,2,1],
                                [604,3,1],
                                [603,4,2],
                                [602,4,3],
                                [601,4,4],
                                [709,1,4],
                                [708,1,3],
                                [707,1,2],
                                [706,2,2],
                                [705,2,2],
                                [704,3,2],
                                [703,3,2],
                                [702,3,3],
                                [701,3,4],
                                [809,1,4],
                                [808,1,3],
                                [807,1,2],
                                [806,2,2],
                                [805,2,2],
                                [804,2,2],
                                [803,3,2],
                                [802,3,3],
                                [801,3,4],
                                [908,1,3],
                                [907,1,3],
                                [906,2,3],
                                [905,2,3],
                                [904,2,3],
                                [903,3,3],
                                [902,3,3],
                                [1005,2,5]])

    # Egyéb függvények...
    def getRandomAction(self):
        actdict = {0: "0", 1: "+", 2: "-"}
        r = np.random.randint(0, 3, 2)
        action = ""
        for act in r:
            action += actdict[act]

        return action
    
    def makeMove(self,jsonData):
        if self.oldpos is not None:
            if tuple(self.oldpos) == tuple(jsonData["pos"]):
                self.oldcounter += 1
            else:
                self.oldcounter = 0
        if jsonData["active"]:
            self.oldpos = jsonData["pos"].copy()

        dir_vals=np.zeros((9,1))
        dir_probs=np.zeros((9,1))
        
        walls=[]
        
        if (jsonData["pos"][0]>0 and jsonData["pos"][1]>0): #ezeka  részek azért vannak, hogy nagyobb valoszinuseggel menjen az agent a páyla közepe fele
            dir_probs[5,0] += self.w_tomiddle
            rand_dir=5
        elif (jsonData["pos"][0]>0 and jsonData["pos"][1]==0):
            dir_probs[6,0] += self.w_tomiddle
            rand_dir=6
        elif (jsonData["pos"][0]>0 and jsonData["pos"][1]<0):
            dir_probs[7,0] += self.w_tomiddle
            rand_dir=7
        elif (jsonData["pos"][0]==0 and jsonData["pos"][1]<0):
            dir_probs[0,0] += self.w_tomiddle
            rand_dir=0
        elif (jsonData["pos"][0]<0 and jsonData["pos"][1]<0):
            dir_probs[1,0] += self.w_tomiddle
            rand_dir=1
        elif (jsonData["pos"][0]<0 and jsonData["pos"][1]==0):
            dir_probs[2,0] += self.w_tomiddle
            rand_dir=2
        elif (jsonData["pos"][0]<0 and jsonData["pos"][1]>0):
            dir_probs[3,0] += self.w_tomiddle
            rand_dir=3
        elif (jsonData["pos"][0]==0 and jsonData["pos"][1]>0):
            dir_probs[4,0] += self.w_tomiddle
            rand_dir=4
            
        for field in jsonData["vision"]: #végigmegyünk a látóemző pixelein
            if not(tuple(field["relative_coord"]) == (0, 0)): #a 80 pontot nézük a környezetünkben
                x=int(field["relative_coord"][0])+5 #relativ koordináták eltolása
                y=int(field["relative_coord"][1])+5
                index = np.where(self.cord_inf[:,0]==(x*100+y))[0][0] #look up table melyik sorát nézzük
                octet = self.cord_inf[index,1] #melyik octettben van a vizsgált pixel
                dist = self.cord_inf[index,2] #milyen messze van a vizsgált pixel
        
                if field["value"]==9: #ha fal van az adott pixelen
                    val = -self.w_wall
                    if (tuple(field["relative_coord"]) == (0, 1)): #megnézzük a közvetlen környezetünk: arra biztos nem tudunk menni amerre fal van
                        walls.append(0)
                        dir_probs[0,0]-=100
                    elif(tuple(field["relative_coord"]) == (1, 1)):
                        walls.append(1)
                        dir_probs[1,0]-=100
                    elif(tuple(field["relative_coord"]) == (1, 0)):
                        walls.append(2)
                        dir_probs[2,0]-=100
                    elif(tuple(field["relative_coord"]) == (1, -1)):
                        walls.append(3)
                        dir_probs[3,0]-=100
                    elif(tuple(field["relative_coord"]) == (0, -1)):
                        walls.append(4)
                        dir_probs[4,0]-=100
                    elif(tuple(field["relative_coord"]) == (-1, -1)):
                        walls.append(5)
                        dir_probs[5,0]-=100
                    elif(tuple(field["relative_coord"]) == (-1, 0)):
                        walls.append(6)
                        dir_probs[6,0]-=100
                    elif(tuple(field["relative_coord"]) == (-1, 1)):
                        walls.append(7)
                        dir_probs[7,0]-=100
    
                elif field["player"] is not None: #ha játékos van az adott pixelen
                    if (field["player"]["size"] <= jsonData["size"]): #ha kisebb mint mi
                        val = self.w_chase * (jsonData["size"]) - (field["player"]["size"]) #ez pozitív érték lesz
                    
                    elif field["player"]["size"] > jsonData["size"]: #ha nagyobb mint mi
                        val = self.w_escape * (jsonData["size"]) - (field["player"]["size"]) #ez negatív érték lesz
                
                else:
                    val = field["value"] #ha kaja vagy semmi
    
                dir_vals[octet,0] += val/(dist*self.w_dist) #a különböző értékeket a távolságokkal sulyozzuk és besoroljuk a megfelelő octettbe

            else: #a 0,0 pont mi vagyunk
                if field["value"] == 9: #ha falon állunk
                    val = -self.w_wall
                else:
                    val=field["value"] #amugy semmi, vagy kaja
                dir_vals[8,0] = val
                
        walls=np.array(walls) #melyik környező cellákon van fal
        
        #az adott irányba az adott octettet és annak két legközelebbi és két egyel távolabbi szomszédját vesszük figyelembe
        dir_probs[0,0]+=dir_vals[0,0] + self.w_neighbor1*(dir_vals[7,0]+dir_vals[1,0]) + self.w_neighbor2*(dir_vals[6,0]+dir_vals[2,0])
        dir_probs[1,0]+=dir_vals[1,0] + self.w_neighbor1*(dir_vals[0,0]+dir_vals[2,0]) + self.w_neighbor2*(dir_vals[7,0]+dir_vals[3,0])
        for i in range(2,6):
            dir_probs[i]+=dir_vals[i,0] + self.w_neighbor1*(dir_vals[i+1,0]+dir_vals[i-1,0]) + self.w_neighbor2*(dir_vals[i+2,0]+dir_vals[i-2,0])
        dir_probs[6,0]+=dir_vals[6,0] + self.w_neighbor1*(dir_vals[5,0]+dir_vals[7,0]) + self.w_neighbor2*(dir_vals[0,0]+dir_vals[4,0])
        dir_probs[7,0]+=dir_vals[7,0] + self.w_neighbor1*(dir_vals[6,0]+dir_vals[0,0]) + self.w_neighbor2*(dir_vals[5,0]+dir_vals[1,0])
        #a maradásnál csak azt az egy pixelt nézzük de ezt felsúlyozzuk
        dir_probs[8,0] += self.w_stay*dir_vals[8,0]
        
        #ne menjünk vissza oda ahonnan jöttünk
        i=self.direction_prev
        if i>3:
            i-=8
        i+=4
        dir_probs[i,0] -= 100
        
        direction = int(np.argmax(dir_probs)) #a legnagyobb összegű irányba megyünk
        
        if dir_probs[direction,0] <= self.w_stuck: #kivéve ha a legnagyobb összeg is túl kicsi => ekkor rossz környéken vagyunk, tehát proóbáljunk meg kijutni innen
            no_wall= False #amig nem találunk olyan irányt amerre nincs fal
            while not no_wall:
                if (np.where(walls==self.constdir)[0]).size==0: #ha nincs fal az előzőleg meghatározott irányba, akkor menjünk arra
                    no_wall=True
                elif (np.where(walls==int(rand_dir))[0]).size==0: #ha az előző irányban fal volt, akkor próbáljunk meg középre menni
                    self.constdir=int(rand_dir)
                    no_wall=True
                else: #a közép fele is fal volt, akkor válaszzunk egy random irányt
                    self.constdir = int(np.random.randint(0, 7, 1)) #ha erre is fal van, akkor megint válasszunk egy randomot
                    
            direction=int(self.constdir) #az új irányt adjuk át meggelelő változónak
            
        self.direction_prev=direction
            
        return direction

    # Az egyetlen kötelező elem: A játékmestertől jövő információt feldolgozó és választ elküldő függvény
    def processObservation(self, fulljson, sendData):
        """
        :param fulljson: A játékmestertől érkező JSON dict-be konvertálva.
        Két kötelező kulccsal: 'type' (leaderBoard, readyToStart, started, gameData, serverClose) és 'payload' (az üzenet adatrésze).
        'leaderBoard' type a játék végét jelzi, a payload tartalma {'ticks': a játék hossza tickekben, 'players':[{'name': jáétékosnév, 'active': él-e a játékos?, 'maxSize': a legnagyobb elért méret a játék során},...]}
        'readyToStart' type esetén a szerver az indító üzenetre vár esetén, a payload üres (None)
        'started' type esetén a játék elindul, tickLength-enként kiküldés és akciófogadás várható payload {'tickLength': egy tick hossza }
        'gameData' type esetén az üzenet a játékos által elérhető információkat küldi, a payload:
                                    {"pos": abszolút pozíció a térképen, "tick": az aktuális tick sorszáma, "active": a saját életünk állapota,
                                    "size": saját méret,
                                    "leaderBoard": {'ticks': a játék hossza tickekben eddig, 'players':[{'name': jáétékosnév, 'active': él-e a játékos?, 'maxSize': a legnagyobb elért méret a játék során eddig},...]},
                                    "vision": [{"relative_coord": az adott megfigyelt mező relatív koordinátája,
                                                                    "value": az adott megfigyelt mező értéke (0-3,9),
                                                                    "player": None, ha nincs aktív játékos, vagy
                                                                            {name: a mezőn álló játékos neve, size: a mezőn álló játékos mérete}},...] }
        'serverClose' type esetén a játékmester szabályos, vagy hiba okozta bezáródásáról értesülünk, a payload üres (None)
        :param sendData: A kliens adatküldő függvénye, JSON formátumú str bemenetet vár, melyet a játékmester felé továbbít.
        Az elküldött adat struktúrája {"command": Parancs típusa, "name": A küldő azonosítója, "payload": az üzenet adatrésze}
        Elérhető parancsok:
        'SetName' A kliens felregisztrálja a saját nevét a szervernek, enélkül a nevünkhöz tartozó üzenetek nem térnek vissza.
                 Tiltott nevek: a configban megadott játékmester név és az 'all'.
        'SetAction' Ebben az esetben a payload az akció string, amely két karaktert tartalmaz az X és az Y koordináták (matematikai mátrix indexelés) menti elmozdulásra.
                a karakterek értékei '0': helybenmaradás az adott tengely mentén, '+' pozitív irányú lépés, '-' negatív irányú lépés lehet. Amennyiben egy tick ideje alatt
                nem külünk értéket az alapértelmezett '00' kerül végrehajtásra.
        'GameControl' üzeneteket csak a Config.py-ban megadott játékmester névvel lehet küldeni, ezek a játékmenetet befolyásoló üzenetek.
                A payload az üzenet típusát (type), valamint az ahhoz tartozó 'data' adatokat kell, hogy tartalmazza.
                    'start' type elindítja a játékot egy "readyToStart" üzenetet küldött játék esetén, 'data' mezője üres (None)
                    'reset' type egy játék után várakozó 'leaderBoard'-ot küldött játékot állít alaphelyzetbe. A 'data' mező
                            {'mapPath':None, vagy elérési útvonal, 'updateMapPath': None, vagy elérési útvonal} formátumú, ahol None
                            esetén az előző pálya és növekedési map kerül megtartásra, míg elérési útvonal megadása esetén új pálya kerül betöltésre annak megfelelően.
                    'interrupt' type esetén a 'data' mező üres (None), ez megszakítja a szerver futását és szabályosan leállítja azt.
        :return:
        """
        #konstans adatok a koordinátákról egy numpy arraybe
        
        # Játék rendezéssel kapcsolatos üzenetek lekezelése
        if fulljson["type"] == "leaderBoard":
            
            #print("Game finished after",fulljson["payload"]["ticks"],"ticks!")
            #print("Leaderboard:")
            for score in fulljson["payload"]["players"]:
                #print(score["name"],score["active"], score["maxSize"])
                if score["name"] == "RemotePlayer":
                    w=[self.w_dist, self.w_stay, self.w_wall, self.w_neighbor1, self.w_neighbor2, self.w_chase, self.w_escape, self.w_stuck, self.w_tomiddle]
                    self.w_dist, self.w_stay, self.w_wall, self.w_neighbor1, self.w_neighbor2, self.w_chase, self.w_escape, self.w_stuck, self.w_tomiddle, self.map_cnt = Evolution.evolution(w,score["maxSize"],alpha=0.2, chance=0.1)
                    "./maps/" + self.maps[self.map_cnt]
                
            sendData(json.dumps({"command": "GameControl", "name": "master",
                                 "payload": {"type": "reset", "data": {"mapPath": ("./maps/" + self.maps[self.map_cnt]), "updateMapPath": ("./maps/" + self.maps[self.map_cnt])}}}))
            
            
        if fulljson["type"] == "readyToStart":
            
            #print("Game is ready, starting in 5")
            
            sendData(json.dumps({"command": "GameControl", "name": "master",
                                 "payload": {"type": "start", "data": None}}))

        #if fulljson["type"] == "started":
            #print("Startup message from server.")
            #print("Ticks interval is:",fulljson["payload"]["tickLength"])


        # Akció előállítása bemenetek alapján (egyezik a NaiveHunterBot-okéval)
        elif fulljson["type"] == "gameData":
            jsonData = fulljson["payload"]
            if "pos" in jsonData.keys() and "tick" in jsonData.keys() and "active" in jsonData.keys() and "size" in jsonData.keys() and "vision" in jsonData.keys():
                
                #pozicíót számítunk a sulyok és bemenetek segítségével
                direction=self.makeMove(jsonData)
                
                actstring="00"
                if(not direction):
                    actstring = "0+"
                elif direction==1:
                    actstring = "++"
                elif direction==2:
                    actstring = "+0"
                elif direction==3:
                    actstring = "+-"
                elif direction==4:
                    actstring = "0-"
                elif direction==5:
                    actstring = "--"
                elif direction==6:
                    actstring = "-0"
                elif direction==7:
                    actstring = "-+"
                elif direction==8:
                    #actstring = self.getRandomAction()
                    actstring = "00"
                        
                # Akció JSON előállítása és elküldése
                sendData(json.dumps({"command": "SetAction", "name": "RemotePlayer", "payload": actstring}))
            


if __name__=="__main__":
    # Példányosított stratégia objektum
    hunter = RemoteNaiveHunterStrategy()
    
    seed(42) # random generátor seed-je
    
    # Socket kliens, melynek a szerver címét kell megadni (IP, port), illetve a callback függvényt, melynek szignatúrája a fenti
    # callback(fulljson, sendData)
    client = SocketClient("localhost", 42069, hunter.processObservation)

    # Kliens indítása
    client.start()
    # Kis szünet, hogy a kapcsolat felépülhessen, a start nem blockol, a kliens külső szálon fut
    time.sleep(0.01)
    # Regisztráció a megfelelő névvel
    client.sendData(json.dumps({"command": "SetName", "name": "RemotePlayer", "payload": None}))

    # Nincs blokkoló hívás, a főszál várakozó állapotba kerül, itt végrehajthatók egyéb műveletek a kliens automata működésétől függetlenül.