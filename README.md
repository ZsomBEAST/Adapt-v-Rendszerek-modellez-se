# Adaptív Rendszerek Modellezése
Projekt házi feladat

## Döntéshozó algoritmus

Az AdaptIO az "Adaptív rendszerek modellezése" tárgyhoz készült házi feladat Szalay János Zsombor (FONP0O) és Molnár András Zsolt (RUMGQT) által készített megoldása.
A házi feladat egy paraméterekkel rendelkező algoritmus. Az alapgondolot a már előre megvalósított NaiveHunter algoritmusból indult.

Az agent 8 irányba mozdulhat el a jelenelgi helyzetéből. Ennek megfelelően a látoteret 8 egyenlő területű oktettre osztottuk

![image](https://user-images.githubusercontent.com/62031988/168669957-90a64183-3e68-4bdc-bf76-61ac9d6380fb.png)

Minden relatív koordinátához pontosan egy octett tartozik. Az octettekhez sulyozott összegek segítségével értéket rendelhetünk. Az ételek értéke egyértelműen alakul a feladatkiirás alapján. A **falak értéke** egy tanulható paraméter lesz (de azt tudjuk, hogy biztosan negatív). Az adott mező sulyát az összegzésnél a távolsága határozza meg az agent-től.

![image](https://user-images.githubusercontent.com/62031988/168672805-e2d0bb01-56c4-4965-9075-783361ff68f2.png)

Az ellenfelek méretét mindig a mi méretünkhöz hasonlítjuk. A méretkülönbséget egy **üldözési parméterrel** szorozzuk (+ szám), ha az ellenfél kisebb nálunk, ha pedig nagyobb mint mi akkor egy **menekülési paraméterrel** (- szám). Az érték az ellenfél relatív koordinátájának megfelelő octetthez fog tartozni.

A távolságok még egy **távolságskálázó**, tanulható paraméterrel is megszorzásra kerülnek. Így optimális mértékben vehetjük figyelembe, az objektumok távolságát.
A relatív koordinátákhoz tartozó octet és távolság egy look up table segítségével elérhető a program számára. Az agent nem mindig mozog. Ha éppen alatta terem étel, akkor megérheti egy helyben maradni. Hogy ez az érték felvehesse a versenyt a sulyozott összegekkel, ezt is megszorozzuk egy tanulható sullyal. Ez a súly tehát az **egyhelyben maradás** valószínűségével van összefüggésben.

A súlyozott összegeket kiszámolva kapunk 8 darab számot (kilencet a helybenmaradással együtt). Az irányválasztáshoz az adott irányhoz tartozó octettett 1 sulyal vesszük figyelembe és a két **közelebbi szomszédját** és a két **távolabbi szomszédját** is egy - egy tanítható sulyparaméter segítségével (1 irányhoz összesen 5 octettet veszünk figyelembe).

Megfigyelhető jelenség, hogy az agent minél hamarabb eljut a pálya közepére annál jobb eredményt ér el. Ez azért van mert általában ott több étel van, illetve ott nincs annyi határoló fal ezért a szabad mozgásra is több a lehetőség. Ezért az irányválasztásnál még egy tanítható paraméter segítségével növeljük annak az iránylehetőségnek az értékét, amely a **középpont felé irányítja** az agent-et.

Amennyiben az agent beragad valamilyen részlegesen zárt területre, valahogy ki kell onnan találni. Ekkor az oktettekben meghatározott irányszámok nem elég nagyok a döntéshez. Ekkor az algoritmus először a pálya közepe felé igyekszik haladni. Amennyiben ez nem lehetséges, akkor random választ irányt, ezt addig tartja, amíg egyértelműen jó értékű oktettet nem talál, vagy falnak nem ütközik, falba ütközés során újra random irányt választ.

![image](https://user-images.githubusercontent.com/62031988/168679521-e6cdee17-c111-4a27-ba96-e2a2f2efb81e.png)

Az agent sosem választ olyan irányt amely irányban a szomszédos mezőn fal van, illetve sosem választja azt az irányt ahonnan előző lépésben jött (beragadást gátló feltételek).

## A tanítás

Az algoritmus paramétereinek optimalizálását/tanítását genetikus algoritmussal végeztük.  Az egyes egyedeket a döntési algoritmushoz tartozó paramétersor reprezeltálja, amelyek valós értékűek.  A genetikus algoritmushoz szükséges fitness függvény az adott számú tick (300) után elért méret, ez
több pályán többszöri futás során kapott átlagérték. A keresztezni kívánt egyedek kiválasztása rulettkerék algoritmussal történik, 
ez annyit jelent, hogy az egyedek fitness értéküknek megfelelő valószínűséggel kerülnek kiválasztásra. Az algoritmushoz kapcsolódó keresztezést valós keresztezéssel valósítottuk meg, a keresztezés során felhasznált paraméter az alpha (0.2). Két szülő hoz létre egy utódot, az egyik szülő paraméterei alpha-szoros, míg a másik szülő (1-alpha)-szoros értékkel öröklődik az utódba. A keresztezést követően az utódokon mutációt hajtunk végre, egy előre meghatározott valószínűségi érték (0.1) alapján, ennek célja, hogy ne ragadjon le lokális optimum megoldásba. A mutáció során ha a mutáció bekövetkezik, akkor egy random számmal kerül megszorzásra az adott egyed adott sulya. A genetikus algoritmus populációja 10 egyedet tartalmaz, ennek korlátja a rendelkezésre álló számítási erőforrás. A keresztezés során 10 utódot hozunk létre, az egyesített populációból a 10 legjobb egyed éli túl. 

A GE algoritmus, mint egy állapotgép lett megvalósítva. A GE algoritmus egy játék kör végén hívódik meg, ekkor menti el a fitness értékét az egyedeknek. A kiindulási populáció random értékekből indul, az algoritmus kiértékeli a szülő populációt majd az algoritmusnak megfelelően elvégzi a genetikus műveleteket. Ezt követően már csak az utód populációt kell kiértékelni, mivel az n-edik szülő populáció megegyezik az (n-1) egyesített populációval, ami tartalmazza fitness értékeket.
