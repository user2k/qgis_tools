# -*- coding: utf-8 -*-

"""
***************************************************************************
    qgis_tools.py
    ---------------------
    Date                 : May 2024
    Copyright            : (C) 2024 by Mike Kozdronkiewicz
    Email                : user2k@gmail.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

DESCRIPTION

    Biblioteka do pracy z qgisem, zawiera funkcje do obracania linii, łączenia linii, określania styczności linii
    Wymaga zainstalowanego qgis w systemie, ścieżek wyszukiwania w vs do bibliotek pythona w qgisie
    Funkcje przerabiaja upierdliwe QgsGeometry na bardziej przyjazne QgsLineString
    
    Specjalne podziekowania dla copilota za 1000 błędów w kodzie, ale i nieocenioną pomoc w pisaniu :)
    
"""
# qgis_works.py

#importujemy bibliotekę qgis

from qgis.core import *

#tworzymy line3d

#subclass dla vertexAt żeby przyjmował 1 argument int i wykonuje vertexAt(QgsVertexId(1,1,argument))
#przyjmujemy że wszystkie obiekty są 1 cześciowe

class QgsLineString(QgsLineString):
    def vertexAt(self, i):
        return super().vertexAt(QgsVertexId(1,1,i))

    def deleteVertex(self, i) -> bool:
        return super().deleteVertex(QgsVertexId(1,1,i))

class qgis_tools:
    
    #inicjalizacja
    def __init__(self):
        pass
    
    #obracanie linii linia musi być QgsLineString lub QgsGeometry
    
    def obroc_linie(self, line):
        geomtype = False
        # jezeli line to qgsgeometry to zamien na QgsLineString
        if type(line).__name__ == 'QgsGeometry':
            line2 = QgsLineString()
            line2.fromWkt(line.asWkt())
            line = line2
            geomtype = True

        # jezeli line to nie jest QgsLineString to zwróć błąd
        if type(line).__name__ != 'QgsLineString':
            return 'Error: nie moge stworzyc linestring' 
        
        line2 = QgsLineString()

        for i in range(line.vertexCount()):
            line2.addVertex(line.vertexAt(line.vertexCount()-i-1))
        # jeżeli line to qgsgeometry to zamien na QgsGeometry
        if geomtype:
            return QgsGeometry.fromWkt(line2.asWkt())
        return line2

    def gdzie_styczne(self, line1 :QgsLineString, line2 :QgsLineString, bufl :float):
        # funkcja zwraca PP PK KP KK w zależności od tego gdzie linie sie stykają w odleglości bufora bufl
        
        output = ''

        # jezeli line to qgsgeometry to zamien na QgsLineString
        if type(line1).__name__ == 'QgsGeometry':
            line1 = QgsLineString().fromWkt(line1.asWkt())
        if type(line2).__name__ == 'QgsGeometry':
            line2 = QgsLineString().fromWkt(line2.asWkt())
        
        # jezeli line to nie jest QgsLineString to zwróć błąd
        if type(line1).__name__ != 'QgsLineString' or type(line2).__name__ != 'QgsLineString':
            return 'Error: nie moge stworzyc linestring' 
        
        print(line1.vertexAt(0).distance(line2.vertexAt(0)))
        print(line1.vertexAt(0).distance(line2.vertexAt(line2.vertexCount()-1)))
        print(line1.vertexAt(line1.vertexCount()-1).distance(line2.vertexAt(0)))
        print(line1.vertexAt(line1.vertexCount()-1).distance(line2.vertexAt(line2.vertexCount()-1)))
        
        if line1.vertexAt(0).distance(line2.vertexAt(0)) <= bufl:
            output = output + 'PP'
        elif line1.vertexAt(0).distance(line2.vertexAt(line2.vertexCount()-1)) <= bufl:
            output = output + 'PK'
        elif line1.vertexAt(line1.vertexCount()-1).distance(line2.vertexAt(0)) <= bufl:
            output = output + 'KP'
        elif line1.vertexAt(line1.vertexCount()-1).distance(line2.vertexAt(line2.vertexCount()-1)) <= bufl:
            output = output + 'KK'
        # jeżeli długość output nie równa się 2 to zwróć błąd
        if len(output) != 2:
            print(output)
            return 'Error: nie moge okreslic stycznosci'
        return output

    def polacz_linie(self, line1 :QgsLineString, line2 :QgsLineString, bufl :float):
        # funkcja zwraca polaczenie linii w zależności od tego gdzie linie sie stykają w odleglości bufora bufl
        
        geomtype = False
        # jezeli line to qgsgeometry to zamien na QgsLineString
        if type(line1).__name__ == 'QgsGeometry':
            line1 = QgsLineString().fromWkt(line1.asWkt())
            geomtype = True
        if type(line2).__name__ == 'QgsGeometry':
            line2 = QgsLineString().fromWkt(line2.asWkt())
        
        # jezeli line to nie jest QgsLineString to zwróć błąd
        if type(line1).__name__ != 'QgsLineString' or type(line2).__name__ != 'QgsLineString':
            return 'Error: nie moge stworzyc linestring' 
        
        styczne = self.gdzie_styczne(line1, line2, bufl)
        # jeżeli retval zawiera Error to zwróć błąd
        if 'Error' in styczne:
            return styczne

        if styczne == 'PP':
            # obracamy line2
            line1 = self.obroc_linie(line1)
        elif styczne == 'PK':
            # obracamy line1 i line2
            print('obracam obie linie')
            line1 = self.obroc_linie(line1)
            line2 = self.obroc_linie(line2)
            print(line1.asWkt())
            print(line2.asWkt())
            
        elif styczne == 'KP':
            # wszystko ok
            pass
        elif styczne == 'KK':
            # obracamy line2
            line2 = self.obroc_linie(line2)
        
        # pobieramy ostatni punkt z line1 i pierwszy z line2
        l1k = line1.vertexAt(line1.vertexCount()-1)
        l2p = line2.vertexAt(0)
            
        # porównujemy czy punkty są dokładnie takie same
        if l1k.x() == l2p.x() and l1k.y() == l2p.y():
            # dodajemy bez 1 punktu z line2
            for i in range(1, line2.vertexCount()):
                line1.addVertex(line2.vertexAt(i))
            # dodajemy wszystkie punkty z line2
        else:
            for i in range(line2.vertexCount()):
                line1.addVertex(line2.vertexAt(i))
            
        # jeżeli line1 to qgsgeometry to zamien na QgsGeometry
        if geomtype:
            return QgsGeometry.fromWkt(line1.asWkt())
        return line1

    def __del__(self):
        pass

qt = qgis_tools()

# tworzymy sample line1


#tworzymy sample line2 zlożona z 3 punktów
line2 = QgsLineString([QgsPoint(10,9,0),  QgsPoint(30,30,0)])
line1 = QgsLineString([QgsPoint(50,50,0), QgsPoint(10,9,0)])

print(line1.asWkt())
print(line2.asWkt())
print(qt.gdzie_styczne(line1, line2, 1.1))

rv = qt.polacz_linie(line1,line2,1.1)
#jeżeli zwróci Error to wypisz błąd
if 'Error' in rv:
    print(rv)
else:
    print(rv.asWkt())

#create sample qgsgeometry object
#qgsgeom = QgsGeometry.fromWkt(line1.asWkt())
#print(qgsgeom.asWkt())
#print(qt.obroc_linie(qgsgeom).asWkt())
