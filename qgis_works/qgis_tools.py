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
    Aktualnie funkcje pracują na qgsgeometry
    
"""
# qgis_tools.py

#importujemy bibliotekę qgis

from qgis.core import *

class qgis_tools:
    
    #inicjalizacja
    def __init__(self):
        pass
    
    #destruktor
    def __del__(self):
        pass    
    
    # funkcja odwraca punkty w QgsGeometry typu linia

    def reverse_line(self, line:QgsGeometry):
        
        # sprawdz czy tym geometrii to linia
        if line.type() != QgsWkbTypes.LineGeometry:
            return 'Error: nie jest to geometria liniowa'
        # tworzymy nową geometrię typu linia
        new_line = QgsGeometry(line)
        # odwracamy linie
        for i in range (0, line.constGet().vertexCount()):
            new_line.moveVertex(line.vertexAt(i),line.constGet().vertexCount()-1-i)
        return new_line

    # funkcja sprawdza czy linie dotykają się na poczatku lub koncu i zwraca SE SS ES EE
    
    def touch_lines(self, line1:QgsGeometry, line2:QgsGeometry, buf:float):
        # sprawdz czy tym geometrii to linia
        
        touchin = ''
        if line1.type() != QgsWkbTypes.LineGeometry or line2.type() != QgsWkbTypes.LineGeometry:
            return 'Error: nie jest to geometria liniowa'
        # sprawdz czy linie mają punkty początkowe i końcowe w odległości mniejszej niż buf
        if line1.vertexAt(0).distance(line2.vertexAt(0)) <= buf:
            touchin = touchin + 'SS'
        if line1.vertexAt(0).distance(line2.vertexAt(line2.constGet().vertexCount()-1)) <= buf:
            touchin = touchin + 'SE'
        if line1.vertexAt(line1.constGet().vertexCount()-1).distance(line2.vertexAt(0)) <= buf:
            touchin = touchin + 'ES'
        if line1.vertexAt(line1.constGet().vertexCount()-1).distance(line2.vertexAt(line2.constGet().vertexCount()-1)) <= buf:
            touchin = touchin + 'EE'
        
        if len(touchin) == 0:
            return 'Error: Nie ma styczności'
        elif len(touchin) > 2:
            return 'Error: Za dużo styczności'      
        return touchin

    # funkcja łączy linie w jedną linię
    def merge_lines(self, line1:QgsGeometry, line2:QgsGeometry, buf:float):
        
        # sprawdz czy tym geometrii to linia
        if line1.type() != QgsWkbTypes.LineGeometry or line2.type() != QgsWkbTypes.LineGeometry:
            return 'Error: nie jest to geometria liniowa'
        
        touching = self.touch_lines(line1, line2, buf)
        
        if 'Error' in touching:
            return touching
        
        if touching == 'SS':
            # obracamy pierwszą linie
            line1 = self.reverse_line(line1)
        elif touching == 'ES':
            pass
        elif touching == 'SE':
            # obracamy obie linie
            line1 = self.reverse_line(line1)    
            line2 = self.reverse_line(line2)
        elif touching == 'EE':
            # obracamy drugą linie
            line2 = self.reverse_line(line2)
        
        # tworzymy nową geometrię typu linia z line2
        new_line = QgsGeometry(line2)
        #pobieramy punkt koncowy line1
        lend_point = line1.vertexAt(line1.constGet().vertexCount()-1)
        #pobieramy punk poczatkowy lini2
        lstart_point = line2.vertexAt(0)

        iend = line1.constGet().vertexCount()-1
        # sprawdzamy czy punkty są takie same 
        if lend_point.distance(lstart_point)==0:
            iend = iend - 1
            
        # dodajemy punkty z pierwszej linii
        # z jakiegos magicznego powodu nie mozemy dodac punktu po ostatnim :)  
        for i in range (iend, -1, -1):
            new_line.insertVertex(line1.vertexAt(i),0)
        return new_line

# testy

qt = qgis_tools()

geom = QgsGeometry.fromWkt('LINESTRING(0 0 0, 1 1 0 , 2 2 0 , 3 3 0)')
geom2 = QgsGeometry.fromWkt('LINESTRING(4 4 0, 3 3 0)')
print ('original geom = ' + geom.asWkt())
print ('original geom2 = ' + geom2.asWkt())
print ('reversed geom = '  + qt.reverse_line(geom).asWkt())
print ('reversed geom2 = '  + qt.reverse_line(geom2).asWkt())

print('geom and geom 2 touches by (buflen = 0.5) = ' + qt.touch_lines(geom,geom2,0.5))
print('geom and geom merge in (buflen = 0.5) = ' + qt.merge_lines(geom,geom2,0.5).asWkt())





