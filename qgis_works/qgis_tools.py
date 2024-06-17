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

    Biblioteka powinna dzialac na QgsGeometry 2D i 3D

    Biblioteka do pracy z qgisem, zawiera funkcje do 
    -obracania linii (punkty nie kąt obrotu), 
    -łączenia linii, 
    -dzielenia linii z dociaganiem i bez dociagania punktów na linii,
    -określania styczności linii
    -wspolpraca z QgsLayer i QgsFeature
    -wyszukiwanie features w warstwie po geometrii, buforze i atrybutach
    
    UWAGA:
    Wymaga zainstalowanego qgis w systemie, ścieżek wyszukiwania w vs do bibliotek pythona w qgisie
    Aktualnie funkcje pracują na qgsgeometry, testowane na QGIS 3.36 i Python 3.12
    
"""
# qgis_tools.py

#importujemy bibliotekę qgis

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsApplication


import sys

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
                return 0, -1
            # sprawdz czy tym geometrii to punkt
            if point.type() != QgsWkbTypes.PointGeometry:
                return 0, -1

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
                    return 0, -1
                pw = QgsGeometry(line.vertexAt(vi))
                return pw, vi
            else:
                # obliczamy najblizszy punkt na linii (nie punkt zalamania)
                # pobieramy po 2 punkty linii
                pwin = -1
                pdist = -1
                iwin = -1
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
                            pwin = QgsGeometry(p1)
                            pdist = p1.distance(p3)
                            iwin = i
                    #wiekszy niz 1 czyli za wektorem
                    elif u > 1:
                        if p2.distance(p3) <= tol and (pdist == -1 or pdist > p2.distance(p3)):
                            # typujemy p2
                            pwin = QgsGeometry(p2)
                            pdist = p2.distance(p3)
                            iwin = i+1
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
                            iwin = i
                            
                if pwin == -1:
                    return 0,-1
                else:
                    
                    return pwin, iwin


# podziel linie na dwie linie w punkcie

   
    def split_line(self, line:QgsGeometry, point:QgsGeometry, tol:float, topts:bool = False):
            
            # sprawdz czy tym geometrii to linia
            if line.type() != QgsWkbTypes.LineGeometry:
                return 0
            # sprawdz czy tym geometrii to punkt
            if point.type() != QgsWkbTypes.PointGeometry:
                return 0
            
            # znajdz punkt na linii
            pwin, iwin = self.nearest_point_on_line(line, point, tol, topts)
            
            if pwin == 0:
                return 0
            
            # tworzymy nowe "prawie" puste linie
            # bo nie da sie dodac punktu na koncu linii, albo do linii ktora jest pusta
            line1 = QgsGeometry.fromWkt('LINESTRING(0 0 0,  0 0 0)')
            line2 = QgsGeometry.fromWkt('LINESTRING(0 0 0,  0 0 0)')
            
            # tu zabawa zeby nie dublowac nakladajacych sie punktow
            # lastvalue i newvalue
            
            lv = QgsGeometry(QgsPoint())
            for i in range (0, iwin+1):
                nv = QgsGeometry(line.vertexAt(i))
                if lv.equals(nv) == False:
                    line1.insertVertex(line.vertexAt(i),line1.constGet().vertexCount()-1)
                    lv = nv
            nv = QgsGeometry(pwin.vertexAt(0))
            if lv.equals(nv) == False:
                line1.insertVertex(pwin.vertexAt(0),line1.constGet().vertexCount()-1)
                lv = nv
            
            # lastvalue powinno byc na pwin
            line2.insertVertex(pwin.vertexAt(0),line2.constGet().vertexCount()-1)
            for i in range (iwin+1, line.constGet().vertexCount()):
                nv = QgsGeometry(line.vertexAt(i))
                if lv.equals(nv) == False:
                    line2.insertVertex(line.vertexAt(i),line2.constGet().vertexCount()-1)
                    lv = nv
            wynik = []
            # usuwamy nadmiarowe punkty
            if line1.constGet().vertexCount() > 3:
                line1.deleteVertex(0)
                line1.deleteVertex(line1.constGet().vertexCount()-1)
                wynik.append(line1)
            if line2.constGet().vertexCount() > 3:
                line2.deleteVertex(0)
                line2.deleteVertex(line2.constGet().vertexCount()-1)                
                wynik.append(line2)
            return wynik
    

    # dociagnij linie do punktu (poczatek lub koniec)
    def snap_line_to_point(self, line:QgsGeometry, point:QgsGeometry, tol:float):
        # sprawdz czy tym geometrii to linia
            if line.type() != QgsWkbTypes.LineGeometry:
                return 0
            # sprawdz czy tym geometrii to punkt
            if point.type() != QgsWkbTypes.PointGeometry:
                return 0
            
            line_new = QgsGeometry(line)

            # obliczamy dist do punktu
            dist1 = line.vertexAt(0).distance(point.vertexAt(0))
            dist2 = line.vertexAt(line.constGet().vertexCount()-1).distance(point.vertexAt(0))
            
            # dociagamy do punktu
            if dist1 <= tol:
                line_new.moveVertex(point.vertexAt(0),0)
            elif dist2 <= tol:
                line_new.moveVertex(point.vertexAt(0),line.constGet().vertexCount()-1)
            else:
                return 0
            return line_new
    

    def qgis_find_features_on_layer(self, layer:QgsVectorLayer, geom:QgsGeometry, buffer:float):
        # sprawdzmy czy geometria nie jest albo NULL albo unknown
        
        if geom.isNull() or geom.type() == QgsWkbTypes.Unknown:
            return []
        
        # robimy buffer wokół geometrii
        if buffer == 0:
            buffer = geom
        else:
            buffer = geom.buffer(buffer,5)
            
        # robimy rectangle z buffer
        rect = buffer.boundingBox()
        # pobieramy features z warstwy w prostokącie
        request = QgsFeatureRequest().setFilterRect(rect)
        features = layer.getFeatures(request)
        selection = []
        
        for feature in features:
            if buffer.intersects(feature.geometry()):
                selection.append(feature)
        return selection

    def qgis_find_features_on_layer_by_query(self, layer:QgsVectorLayer, query:str):
        # ustawiamy filtr na warstwie
        features = layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))
        selection = []
        for feature in features:
            selection.append(feature)
        return selection
    
    def qgis_update_features_attribute(self, layer:QgsVectorLayer, features, attribute:str, value):
        # jak nie mozna edytowac warstwy to koniec
        if not layer.isEditable():
            return 1
        layer.startEditing()
        for feature in features:
            feature.setAttribute(attribute, value)
            layer.updateFeature(feature)
        layer.commitChanges()
        return 0
    
    def qgis_update_features_attributes(self, layer:QgsVectorLayer, features, attributes):
        # jak nie mozna edytowac warstwy to koniec
        if not layer.isEditable():
            return 1
        layer.startEditing()
        for feature in features:
            for key, value in attributes.items():
                feature.setAttribute(key, value)
            layer.updateFeature(feature)
        layer.commitChanges()
        return 0
    
    def qgis_copy_feature(self, layer:QgsVectorLayer, feature:QgsFeature, attributes):
        # jak nie mozna edytowac warstwy to koniec
        if not layer.isEditable():
            return 1
        layer.startEditing()
        new_feature = QgsFeature()
        new_feature.setGeometry(feature.geometry())
        for key, value in attributes.items():
            new_feature.setAttribute(key, value)
        layer.addFeature(new_feature)
        layer.commitChanges()
        return 0
    
    def qgis_execute_sql_command(self, layer:QgsVectorLayer, sql:str):
        # jak nie mozna edytowac warstwy to koniec
        if not layer.isEditable():
            return 1
        layer.startEditing()
        layer.dataProvider().executeSql(sql)
        layer.commitChanges()
        return 0
    
    

        

            













