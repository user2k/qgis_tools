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
            return 0
        # tworzymy nową geometrię typu linia
        new_line = QgsGeometry(line)
        # odwracamy linie
        for i in range (0, line.constGet().vertexCount()):
            new_line.moveVertex(line.vertexAt(i),line.constGet().vertexCount()-1-i)
        return new_line

    # funkcja sprawdza czy linie dotykają się na poczatku lub koncu i zwraca SE SS ES EE
   
    def touch_lines(self, line1:QgsGeometry, line2:QgsGeometry, tol:float):
        
        # sprawdz czy tym geometrii to linia
        touching = ''
        if line1.type() != QgsWkbTypes.LineGeometry or line2.type() != QgsWkbTypes.LineGeometry:
            return 0
        # sprawdz czy linie mają punkty początkowe i końcowe w odległości mniejszej niż buf
        if line1.vertexAt(0).distance(line2.vertexAt(0)) <= tol:
            touching = touching + 'SS'
        if line1.vertexAt(0).distance(line2.vertexAt(line2.constGet().vertexCount()-1)) <= tol:
            touching = touching + 'SE'
        if line1.vertexAt(line1.constGet().vertexCount()-1).distance(line2.vertexAt(0)) <= tol:
            touching = touching + 'ES'
        if line1.vertexAt(line1.constGet().vertexCount()-1).distance(line2.vertexAt(line2.constGet().vertexCount()-1)) <= tol:
            touching = touching + 'EE'
        
        if len(touching) == 0:
            return 0
        elif len(touching) > 2:
            return 0
        return touching

    # funkcja łączy linie w jedną linię
    def merge_lines(self, line1:QgsGeometry, line2:QgsGeometry, tol:float):
        
        # sprawdz czy tym geometrii to linia
        if line1.type() != QgsWkbTypes.LineGeometry or line2.type() != QgsWkbTypes.LineGeometry:
            return 0
        
        touching = self.touch_lines(line1, line2, tol)
        
        if touching == 0:
            return 0
        
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
    
    # funkcja łączy list linii w jedną linię (lub wiecej linii)

    def merge_more_lines(self, morelines, tol:float):
        
        # zliczamy linie w tablicy
        n = len(morelines)
        
        # czy kazda geometria w tablicy to linia
        
        for i in range (0, n):
            if morelines[i].type() != QgsWkbTypes.LineGeometry:
                return 0
            
        i = 0
        while i < n:
            j = 0
            while j < n:
                if i != j:
                    retgeom = self.merge_lines(morelines[i], morelines[j], tol)
                    if retgeom != 0:
                        morelines[i] = retgeom
                        del morelines[j]
                        n = n - 1
                        i = 0
                        j = 0
                        break
                j = j + 1
            i = i + 1
            
        return morelines

    # funkcja znajduje najbliższy punkt na linii do punktu    

    def nearest_point_on_line(self, line:QgsGeometry, point:QgsGeometry, tol:float, topts :bool ):
            
        # sprawdz czy tym geometrii to linia
            if line.type() != QgsWkbTypes.LineGeometry:
                return 0
            # sprawdz czy tym geometrii to punkt
            if point.type() != QgsWkbTypes.PointGeometry:
                return 0

            if topts:
                # pobieramy po punkcie z linii
                vi = -1
                vl = -1
                for i in range (0, line.constGet().vertexCount()):
                    if line.vertexAt(i).distance(point.vertexAt(0)) <= tol:
                        if vl == -1 or (vl > 0 and vl > line.vertexAt(i).distance(point.vertexAt(0))):
                            vi = i
                            vl = line.vertexAt(i).distance(point.vertexAt(0))
                if vl == -1:
                    return 0
                return line.vertexAt(vi)
            else:
                # obliczamy najblizszy punkt na linii (nie punkt zalamania)
                # pobieramy po 2 punkty linii
                pwin = -1
                pdist = -1
                for i in range (0, line.constGet().vertexCount()-1):
                    p1 = line.vertexAt(i)
                    p2 = line.vertexAt(i+1)
                    p3 = point.vertexAt(0)
                    # obliczamy odleglosc punktu od wektora
                    d = p1.distance(p2)
                    if d == 0:
                        continue
                    # obliczamy u - współczynnik na wektorze
                    # czyli odleglosc punktu od p1
                    # podzielona przez dlugosc wektora
                    
                    u = ((p3.x()-p1.x())*(p2.x()-p1.x())+(p3.y()-p1.y())*(p2.y()-p1.y()))/(d*d)
                    # mniej niz 0 czyli przed wektorem
                    if u < 0:
                        if p1.distance(p3) <= tol and (pdist == -1 or pdist > p1.distance(p3)):
                            # typujemy p1
                            pwin = p1
                            pdist = p1.distance(p3)
                    #wiekszy niz 1 czyli za wektorem
                    elif u > 1:
                        if p2.distance(p3) <= tol and (pdist == -1 or pdist > p2.distance(p3)):
                            # typujemy p2
                            pwin = p2
                            pdist = p2.distance(p3)
                    # miedzy punktami wektora
                    else:
                        # obliczamy punkt na linii
                        x = p1.x() + u*(p2.x()-p1.x())
                        y = p1.y() + u*(p2.y()-p1.y())
                        # sprawdzamy ile zmiennych ma punkt (2D czy 3D)
                        if p1.is3D():
                            pw = QgsGeometry.fromWkt('POINT('+str(x)+' '+str(y)+' 0)')
                        else:
                            pw = QgsGeometry.fromWkt('POINT('+str(x)+' '+str(y)+')')
                        if pw.vertexAt(0).distance(p3) <= tol and (pdist == -1 or pdist > pw.vertexAt(0).distance(p3)):
                            # typujemy punkt na linii
                            pwin = pw
                            pdist = pw.vertexAt(0).distance(p3)
                            
                if pwin == -1:
                    return 0
                else:
                    return pwin

            
# testy

qt = qgis_tools()

geom = QgsGeometry.fromWkt('LINESTRING(0 0 0, 1 1 0 , 2 2 0 , 3 3 0)')
geom2 = QgsGeometry.fromWkt('LINESTRING(8 4 0, 8 3 0)')
geom3 = QgsGeometry.fromWkt('LINESTRING(8 3 0, 4 4 0)')
geom4 = QgsGeometry.fromWkt('LINESTRING(-1 -1 0, 0 0 0)')

print ('original geom = ' + geom.asWkt())
print ('original geom2 = ' + geom2.asWkt())
    
print ('reversed geom = '  + qt.reverse_line(geom).asWkt())
print ('reversed geom2 = '  + qt.reverse_line(geom2).asWkt())

touching = qt.touch_lines(geom,geom2,0.5)
if touching == 0:
    print('geom and geom 2 do not touch')
else:
    print('geom and geom 2 touches by (buflen = 0.5) = ' + qt.touch_lines(geom,geom2,0.5))
    print('geom and geom merge in (buflen = 0.5) = ' + qt.merge_lines(geom,geom2,0.5).asWkt())

point = QgsGeometry.fromWkt('POINT(0.1 0.2 0)')
print('splitting geom by point = ' + point.asWkt())
pt1 = qt.nearest_point_on_line(geom,point,0.5,False)
print('nearest point on geom to point = ' + pt1.asWkt())
pt2 = qt.nearest_point_on_line(geom,point,0.5,True)
print('nearest point on geom to point = ' + pt2.asWkt())

geoms = [geom,geom2,geom3,geom4]
print('geoms = ' + str(len(geoms)))
for i in range (0, len(geoms)):
    print('geoms['+str(i)+'] = ' + geoms[i].asWkt())

geoms = qt.merge_more_lines(geoms,0.5)

print('geoms = ' + str(len(geoms)))
for i in range (0, len(geoms)):
    print('geoms['+str(i)+'] = ' + geoms[i].asWkt())










