# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ValdationGoogle
                                 A QGIS plugin
 ValdationGoogle
                              -------------------
        begin                : 2016-12-08
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Fidel Serrano/LANCIS
        email                : serranoycandela@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QPixmap, QProgressBar
from qgis.core import *
from qgis.gui import *
import csv
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from ValdationGoogle_dialog import ValdationGoogleDialog
import os.path
import datetime
import os
import math
from PyQt4.QtCore import QVariant


class ValdationGoogle:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ValdationGoogle_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ValdationGoogle')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ValdationGoogle')
        self.toolbar.setObjectName(u'ValdationGoogle')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ValdationGoogle', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = ValdationGoogleDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ValdationGoogle/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ValdationGoogle'),
            callback=self.run,
            parent=self.iface.mainWindow())
			
        self.dlg.urbano.clicked.connect(self.urbanoClicked)
        self.dlg.urbano.setToolTip("when half of the area or more is built up")
        self.dlg.nourbano.clicked.connect(self.noUrbanoClicked)
        self.dlg.nourbano.setToolTip("when less than half of the area is built up")
        #self.dlg.next.clicked.connect(self.nextCuadrito)
        self.dlg.prev.clicked.connect(self.prevCuadrito)
        self.dlg.pointsButton.setIcon(QIcon(':/plugins/ValdationGoogle/settings.png'))
        self.dlg.pointsButton.setToolTip("change sampling points (shapefile in geographic coordinates)")
        self.dlg.pointsButton.clicked.connect(self.selectFile)
        self.dlg.convertingBar.hide()
        self.dlg.prev.setEnabled(False)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ValdationGoogle'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

#    def urbanoClicked(self):
#        self.dlg.label.setText("urbano "+self.dlg.comboBox.currentText())
		
    def UTM(self, long, lat): #returns utm CoordinateReferenceSystem 
        ZoneNumber = int(math.floor((long + 180)/6) + 1)
        if( lat >= 56.0 and lat < 64.0 and long >= 3.0 and long < 12.0 ):
            ZoneNumber = 32
        #Special zones for Svalbard
        if( lat >= 72.0 and lat < 84.0 ):
          if  ( long >= 0.0  and long <  9.0 ):
            ZoneNumber = 31
          elif( long >= 9.0  and long < 21.0 ):
            ZoneNumber = 33
          elif(long >= 21.0 and long < 33.0 ):
            ZoneNumber = 35
          elif(long >= 33.0 and long < 42.0 ):
            ZoneNumber = 37

        if (lat > 0):
            espg = 32600 + ZoneNumber
        else:
            espg = 32700 + ZoneNumber
    
        return QgsCoordinateReferenceSystem(espg,QgsCoordinateReferenceSystem.EpsgCrsId)
		
    def ponEnCualVas(self):
        self.dlg.label.setText(str(self.id + 1) + " of " + str(self.totalDeCuadritos) )
        #self.dlg.progressBar.setValue(self.id)
    def puntoValidado(self, isUrban):
        with open(os.path.join(self.plugin_dir,'log.txt'), 'a') as file:
            now = datetime.datetime.now()
            file.write(str(self.id)+","+now.strftime("%Y-%m-%d %H:%M")+","+ str(self.id) +","+str(isUrban)+b'\n')
    def urbanoClicked(self):
        #self.dlg.label.setText("urbano")
        self.puntoValidado(1)
        #self.cuadritosLayer.selectByExpression("\"FID_1\"='"+str(self.id)+"'")
        self.cuadritosLayer.select([self.id])
        self.cuadritosLayer.startEditing()
        for feat in self.cuadritosLayer.selectedFeatures():
            feat['urban'] = 1
            feat['year'] = self.dlg.comboBox.currentText()
            self.cuadritosLayer.updateFeature(feat)
        
        #Call commit to save the changes
        self.cuadritosLayer.commitChanges()
        self.cuadritosLayer.removeSelection()
        self.iface.mapCanvas().refresh()
        self.nextCuadrito()
    
    
    def noUrbanoClicked(self):
        #self.dlg.label.setText("no urbano")
        self.puntoValidado(0)
        self.cuadritosLayer.select([self.id])
        #self.cuadritosLayer.selectByExpression("\"FID_1\"='"+str(self.id)+"'")
        self.cuadritosLayer.startEditing()
        for feat in self.cuadritosLayer.selectedFeatures():
            feat['urban'] = 0
            feat['year'] = int(self.dlg.comboBox.currentText())
            self.cuadritosLayer.updateFeature(feat)
        
        #Call commit to save the changes
        self.cuadritosLayer.commitChanges()
        self.cuadritosLayer.removeSelection()
        self.iface.mapCanvas().refresh()
        self.nextCuadrito()

    def prevCuadrito(self):
        self.id = self.id - 1
        if (self.id < 1):
            self.dlg.prev.setEnabled(False)
        self.ponEnCualVas()
        
        self.cuadritosLayer.select([self.id])
        #self.cuadritosLayer.selectByExpression("\"FID_1\"='"+str(self.id)+"'")
        box = self.cuadritosLayer.boundingBoxOfSelected()
        self.iface.mapCanvas().setExtent(box)
        self.iface.mapCanvas().zoomOut()
        self.iface.mapCanvas().zoomOut()
        self.iface.mapCanvas().zoomOut()
        self.cuadritosLayer.removeSelection()
        self.iface.mapCanvas().refresh()
        
        


    def nextCuadrito(self):
        #nextLine = self.cuadritosOrdenadosCSV.next()
        self.id = self.id + 1
        
        if (self.id > 0):
            self.dlg.prev.setEnabled(True)
        self.ponEnCualVas()
        #self.cuadritosLayer.selectByExpression("\"FID_1\"='"+str(self.id)+"'")
        self.cuadritosLayer.select([self.id])
        box = self.cuadritosLayer.boundingBoxOfSelected()
        self.iface.mapCanvas().setExtent(box)
        self.iface.mapCanvas().zoomOut()
        self.iface.mapCanvas().zoomOut()
        self.iface.mapCanvas().zoomOut()
        self.cuadritosLayer.removeSelection()
        self.iface.mapCanvas().refresh()

        
    def selectFile(self):
        openFile = QFileDialog()
        fname = QFileDialog.getOpenFileName(self.dlg, 'Open file', 
         '',"shapefiles files (*.shp)")
        self.dlg.label_2.setText("converting points...")
        self.dlg.label.setText("")
        pointsLayer = QgsVectorLayer(fname, "puntos", "ogr")
        pointProvider = pointsLayer.dataProvider()
        fields = pointProvider.fields()
        self.dlg.convertingBar.show()
        
        self.dlg.convertingBar.setValue(0)
        geoCRS = QgsCoordinateReferenceSystem(4326,QgsCoordinateReferenceSystem.EpsgCrsId)
        googleCRS = QgsCoordinateReferenceSystem(3857,QgsCoordinateReferenceSystem.EpsgCrsId)
        polygonsLayer =  QgsVectorLayer('Polygon?crs=EPSG:3857', 'squares_'+os.path.basename(fname)[:-4] , "memory")
        prPolygons = polygonsLayer.dataProvider() 
        prPolygons.addAttributes( fields )
        polygonsLayer.updateFields()
        totalDePuntos = pointsLayer.featureCount()
        self.dlg.convertingBar.setRange(0,totalDePuntos)
        contador = 0
		
        for feature in pointsLayer.getFeatures():
            contador = contador + 1
            self.dlg.convertingBar.setValue(contador)
            thePoint = feature.geometry().asPoint()
            utmCRS = self.UTM(thePoint.x(), thePoint.y())
            toMeters = QgsCoordinateTransform(geoCRS, utmCRS)
            toDegrees = QgsCoordinateTransform(utmCRS, geoCRS)
            toGoogleDegrees = QgsCoordinateTransform(utmCRS, googleCRS)
            thePointUTM = toMeters.transform(thePoint)
            x = thePointUTM.x()
            y = thePointUTM.y()
            leftUTM = x - 15
            rightUTM = x + 15
            upUTM = y + 15
            downUTM = y - 15
            ll = QgsPoint(leftUTM,downUTM) #lower-left
            ur = QgsPoint(rightUTM,upUTM) #upper right
            ul = QgsPoint(leftUTM,upUTM) #upper left
            lr = QgsPoint(rightUTM,downUTM) #lower-right
            llGeo = toGoogleDegrees.transform(ll)
            urGeo = toGoogleDegrees.transform(ur)
            ulGeo = toGoogleDegrees.transform(ul)
            lrGeo = toGoogleDegrees.transform(lr)
            polyGEO = QgsFeature() 
            pointsGEO = [llGeo,ulGeo,urGeo,lrGeo]
            polyGEO.setGeometry(QgsGeometry.fromPolygon([pointsGEO])) #mske the polygon from corner points
            polyGEO.setAttributes(feature.attributes() )
            prPolygons.addFeatures([polyGEO])
            polygonsLayer.updateExtents()
		
        res = prPolygons.addAttributes([QgsField("urban", QVariant.Int), QgsField("year", QVariant.Int)])
        polygonsLayer.updateFields()
        writer = QgsVectorFileWriter.writeAsVectorFormat(polygonsLayer, os.path.join(os.path.dirname(fname),'squares_'+os.path.basename(fname)[:-4]+'.shp'), "UTF-8", None, "ESRI Shapefile")
        QgsMapLayerRegistry.instance().removeMapLayers([self.cuadritosLayer.id()])
        self.cuadritosLayer = QgsVectorLayer(os.path.join(os.path.dirname(fname),'squares_'+os.path.basename(fname)[:-4]+'.shp'), 'squares_'+os.path.basename(fname)[:-4], "ogr") 
        
        QgsMapLayerRegistry.instance().addMapLayers([self.cuadritosLayer])
        self.totalDeCuadritos = self.cuadritosLayer.featureCount()
        #self.dlg.progressBar.setRange(0,self.totalDeCuadritos)
        #self.dlg.progressBar.setValue(0)
        self.cuadritosLayer.loadNamedStyle(os.path.join(self.plugin_dir,'cuadritosStyle.qml'))
        self.project.write()
        self.id = -1
        self.nextCuadrito()
        self.dlg.prev.setEnabled(False)
        self.dlg.convertingBar.hide()
        self.dlg.label_2.setText("")



    def run(self):
        line = "nada"
        try:
            with open(os.path.join(self.plugin_dir,'log.txt'), 'r') as file:
                for linea in file:
                    line = linea
        except:
            print "no hay log"
            
        self.project= QgsProject.instance()
        self.project.read(QFileInfo(os.path.join(self.plugin_dir,"cuadritosProject.qgs")))
        self.iface.mapCanvas().refresh()
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.cuadritosLayer = layer
        print self.cuadritosLayer.source()        
        self.dlg.show()
        self.totalDeCuadritos = self.cuadritosLayer.featureCount()
        self.id = -1
        if line != "nada":
            self.id = int(line.split(",")[0])
        #self.dlg.progressBar.setRange(0,self.totalDeCuadritos)
        #self.dlg.progressBar.setValue(0)
        self.nextCuadrito()
        self.dlg.exec_()
