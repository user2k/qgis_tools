# -*- coding: utf-8 -*-

"""
***************************************************************************
    tests.py
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

    Testy dla qgis_tools.py
    
"""
# tests.py

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from qgis.core import QgsApplication
from qgis_tools import qgis_tools
import sys

def test_geometry_tools():
    
    qt = qgis_tools()

    geom = QgsGeometry.fromWkt('LINESTRING(-1 -1 0, 1 1 0 , 2 2 0 , 3 3 0)')
    geom2 = QgsGeometry.fromWkt('LINESTRING(8 4 0, 8 3 0)')
    geom3 = QgsGeometry.fromWkt('LINESTRING(8 3 0, 4 4 0)')
    geom4 = QgsGeometry.fromWkt('LINESTRING(-1 -1 0, 0 0 0)')
    point = QgsGeometry.fromWkt('POINT(3.5 3.5 0)')

    geom5 = qt.snap_line_to_point(geom,point,0.5)

    print ('\nOryginalne geometrie')
    print ('original geom = ' + geom.asWkt())
    print ('original geom2 = ' + geom2.asWkt())
    print ('original geom3 = ' + geom3.asWkt())
    print ('original geom4 = ' + geom4.asWkt())
    print ('original point = ' + point.asWkt())
    
    print( '\nDociągniecie linii geom do punktu point')
    print ('snapped geom = ' + geom5.asWkt())   

    print ('\nOdwrócone geometrie')    
    print ('reversed geom = '  + qt.reverse_line(geom).asWkt())
    print ('reversed geom2 = '  + qt.reverse_line(geom2).asWkt())
    print ('reversed geom3 = '  + qt.reverse_line(geom3).asWkt())
    print ('reversed geom4 = '  + qt.reverse_line(geom4).asWkt())
    print ('\nCzy linie geom i geom2 się stykają')
    touching = qt.touch_lines(geom,geom2,0.5)
    if touching == 0:
        print(' - geom i geom2 sie nie stykaja')
    else:
        print(' - geom i geom2 sie stykaja na (StartStart | StartEnd | EndStart | EndEnd) ' + touching)

    print ('\nCzy linie geom2 i geom3 się stykają')
    touching = qt.touch_lines(geom2,geom3,0.5)
    if touching == 0:
        print(' - geom2 i geom3 sie nie stykaja')
    else:
        print(' - geom2 i geom3 sie stykaja na (StartStart | StartEnd | EndStart | EndEnd) ' + touching)
    
    print ('\nDzielimy geom w punkcie z dociaganiem 0.5 do punktów na linii')

    print ('original geom = ' + geom.asWkt())
    print ('original point = ' + point.asWkt())
    pt1, iwin = qt.nearest_point_on_line(geom,point,0.5,True)
    if pt1 != 0:
        print('najblizszy punkt  = ' + pt1.asWkt())
        print('index punktu = ' + str(iwin))

        print('-dzielimy linie na dwie')
        lines = qt.split_line(geom,pt1,0.5)
        if lines != 0:
            for i in range (0, len(lines)):
                print('lines['+str(i)+'] = ' + lines[i].asWkt())

        print('-laczymy linie spowrotem')
        lines = qt.merge_more_lines(lines,0.5)
        if lines != 0:
            for i in range (0, len(lines)):
                print('lines['+str(i)+'] = ' + lines[i].asWkt())
    
    print ('\nDzielimy geom w punkcie bez dociagania, z wyjatkiem początku i konca (0.5 do punktów na linii)')
    pt2, iwin2 = qt.nearest_point_on_line(geom,point,0.5,False)
    if pt2 != 0:
        print('najblizszy punkt  = ' + pt2.asWkt())
        print('index punktu = ' + str(iwin2))
    
        print('-dzielimy linie na dwie')
        lines = qt.split_line(geom,pt2,0.5)
        if lines != 0:
            for i in range (0, len(lines)):
                print('lines['+str(i)+'] = ' + lines[i].asWkt())
        print('-laczymy linie spowrotem')
        lines = qt.merge_more_lines(lines,0.5)
        if lines != 0:
            for i in range (0, len(lines)):
                print('lines['+str(i)+'] = ' + lines[i].asWkt())
                

def test_qgis_tools():
    class EventFilter(QObject):
        def eventFilter(self, obj:QWidget, event):
            # jak nacisniety esc
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Escape:
                    # zamknij aplikacje
                        obj.close()
            return False            

    # inicjujemy qgis (musi być zainstalowany w systemie)
           
    from qgis.core import QgsApplication
    qgis_path = "C:\\qgis3362\\apps\\qgis"
    QgsApplication.setPrefixPath(qgis_path, True)
    qgs = QgsApplication([], True)
    qgs.initQgis()

    # ladujemy projekt
    project_path = "C:\\qgis3362\\prj\\test_project.qgz"
    project_instance = QgsProject.instance()
    project_instance.read(project_path)

    # wyszukujemy warstwy na przyszle uzycie

    wo = 0
    wz = 0
    wi = 0
    layers = project_instance.mapLayers()
    for name, layer in layers.items():
        if 'woda_odcinki' in name:
            wo = layer
        if 'wod_zasuwy' in name:
            wz = layer
        if 'wod_inne_wezly' in name:
            wi = layer

    # tworzymy widget (do qgsapp nie da sie dodac przyciskow, dlatego tworzymy widget i dodajemy przyciski do niego)

    qwidget = QWidget()
    qwidget.setWindowTitle('My app')
    qwidget.resize(800,600)
    
    # tworzymy mapke i dodajemy do widgetu (autoresize przy zmianie rozmiaru widgetu)
    canvas = QgsMapCanvas(qwidget)
    canvas.resize(qwidget.size())
    qwidget.resizeEvent = lambda e: canvas.resize(e.size())

    #dodajemy przycisk do widgetu
    button = QPushButton('Close', qwidget)
    button.move(10,10)
    button.clicked.connect(qwidget.close)

    # ustawiamy warstwy na mapce
    canvas.setCanvasColor(Qt.white)
    canvas.setExtent(wo.extent())
    canvas.setLayers([wo,wz,wi])
    qwidget.show()

    # dodajemy event filter
    event_filter = EventFilter()
    qgs.installEventFilter(event_filter)

    # uruchamiamy aplikacje
    sys.exit(qgs.exec_())
    

test_geometry_tools()
test_qgis_tools()