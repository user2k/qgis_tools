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

    Biblioteka do pracy z qgisem, zawiera funkcje do obracania linii, ³¹czenia linii, okreœlania stycznoœci linii
    Wymaga zainstalowanego qgis w systemie, œcie¿ek wyszukiwania w vs do bibliotek pythona w qgisie
    Funkcje przerabiaja upierdliwe QgsGeometry na bardziej przyjazne QgsLineString
    
    Specjalne podziekowania dla copilota za 100 b³êdów w kodzie, ale i nieocenion¹ pomoc w pisaniu :)
    
"""
# qgis_works.py

#importujemy bibliotekê qgis
from re import L
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

#tworzymy line3d

#subclass dla vertexAt ¿eby przyjmowa³ 1 argument int i wykonuje vertexAt(QgsVertexId(1,1,argument))
#przyjmujemy ¿e wszystkie obiekty s¹ 1 czeœciowe

class QgsLineString(QgsLineString):
    def vertexAt(self, i):
        return super().vertexAt(QgsVertexId(1,1,i))

class qgis_tools:
    
    #inicjalizacja
    def __init__(self):
        pass
    
    #obracanie linii linia musi byæ QgsLineString lub QgsGeometry
    
    def obroc_linie(self, line):
        geomtype = False
        # jezeli line to qgsgeometry to zamien na QgsLineString
        if type(line).__name__ == 'QgsGeometry':
            line2 = QgsLineString()
            line2.fromWkt(line.asWkt())
            line = line2
            geomtype = True

        # jezeli line to nie jest QgsLineString to zwróæ b³¹d
        if type(line).__name__ != 'QgsLineString':
            return 'Error: nie moge stworzyc linestring' 
        
        line2 = QgsLineString()

        for i in range(line.vertexCount()):
            line2.addVertex(line.vertexAt(line.vertexCount()-i-1))
            
        if geomtype:
            return QgsGeometry.fromWkt(line2.asWkt())
        return line2

    def gdzie_styczne(self, line1 :QgsLineString, line2 :QgsLineString, bufl :float):
        # funkcja zwraca PP PK KP KK w zale¿noœci od tego gdzie linie sie stykaj¹ w odlegloœci bufora bufl
        
        output = ''

        # jezeli line to qgsgeometry to zamien na QgsLineString
        if type(line1).__name__ == 'QgsGeometry':
            line1 = QgsLineString().fromWkt(line1.asWkt())
        if type(line2).__name__ == 'QgsGeometry':
            line2 = QgsLineString().fromWkt(line2.asWkt())
        
        # jezeli line to nie jest QgsLineString to zwróæ b³¹d
        if type(line1).__name__ != 'QgsLineString' or type(line2).__name__ != 'QgsLineString':
            return 'Error: nie moge stworzyc linestring' 
        
        if line1.vertexAt(0).distance(line2.vertexAt(0)) < bufl:
            output = output + 'PP'
        elif line1.vertexAt(0).distance(line2.vertexAt(line2.vertexCount()-1)) < bufl:
            output = output + 'PK'
        elif line1.vertexAt(line1.vertexCount()-1).distance(line2.vertexAt(0)) < bufl:
            output = output + 'KP'
        elif line1.vertexAt(line1.vertexCount()-1).distance(line2.vertexAt(line2.vertexCount()-1)) < bufl:
            output = output + 'KK'
        print(output)
        # je¿eli d³ugoœæ output nie równa siê 2 to zwróæ b³¹d
        if len(output) != 2:
            return 'Error: nie moge okreslic stycznosci'
        return output

    def polacz_linie(self, line1 :QgsLineString, line2 :QgsLineString, bufl :float):
        # funkcja zwraca polaczenie linii w zale¿noœci od tego gdzie linie sie stykaj¹ w odlegloœci bufora bufl
        
        output = QgsLineString()

        # jezeli line to qgsgeometry to zamien na QgsLineString
        if type(line1).__name__ == 'QgsGeometry':
            line1 = QgsLineString().fromWkt(line1.asWkt())
        if type(line2).__name__ == 'QgsGeometry':
            line2 = QgsLineString().fromWkt(line2.asWkt())
        
        # jezeli line to nie jest QgsLineString to zwróæ b³¹d
        if type(line1).__name__ != 'QgsLineString' or type(line2).__name__ != 'QgsLineString':
            return 'Error: nie moge stworzyc linestring' 
        
        styczne = self.gdzie_styczne(line1, line2, bufl)
        # je¿eli retval zawiera Error to zwróæ b³¹d
        if 'Error' in styczne:
            return styczne
        
        if styczne == 'PP':
            

        return line1

    def __del__(self):
        pass

qt = qgis_tools()

# tworzymy sample line1


#tworzymy sample line2 zlo¿ona z 3 punktów w 1 linii kodu
line1 = QgsLineString([QgsPoint(10,10,0), QgsPoint(20,20,0), QgsPoint(30,30,0)])
line2 = QgsLineString([QgsPoint(50,50,0), QgsPoint(40,40,0), QgsPoint(10,10,0)])

print(line1.asWkt())
print(line2.asWkt())

print(qt.gdzie_styczne(line1, line2, 0.1))
print(qt.polacz_linie(line1,line2,0.1).asWkt())

#create sample qgsgeometry object
#qgsgeom = QgsGeometry.fromWkt(line1.asWkt())
#print(qgsgeom.asWkt())
#print(qt.obroc_linie(qgsgeom).asWkt())






