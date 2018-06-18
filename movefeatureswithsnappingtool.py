# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class MoveFeaturesWithSnappingTool(QgsMapTool):

    def __init__(self, canvas,iface):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.rb = None
        self.count = 0
        self.featid = None
        self.snapping = True
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #faed55",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))


    def move_features(self):
        layer = self.canvas.currentLayer()
        self.check_crs()
        if self.layerCRSSrsid != self.projectCRSSrsid:
            QMessageBox.warning(None, "Warning", "Different Coordinate with map and layer! Nothing done.")
            return
        geom = self.rb.asGeometry()
        polyline = geom.asPolyline()
        points = [QgsPoint(pair[0], pair[1]) for pair in polyline]
        deltax = points[1].x() - points[0].x()
        deltay = points[1].y() - points[0].y()
        for feature in layer.selectedFeatures():
            layer.translateFeature(feature.id(), deltax, deltay)

    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()
        if not layer:
            return
        pnt = self.getSnapPoint(event,layer)
        self.rb.addPoint(pnt) #最初のポイントは同じ点が2つ追加される仕様？
        self.startmarker.setCenter(pnt)
        self.startmarker.show()
        self.count= self.count+1

    def getSnapPoint(self,event,layer):
        result = []
        self.snapmarker.hide()
        x = event.pos().x()
        y = event.pos().y()
        if self.snapping:
            startingPoint = QPoint(x, y)
            snapper = QgsMapCanvasSnapper(self.canvas)
            (retval, result) = snapper.snapToCurrentLayer(startingPoint,QgsSnapper.SnapToVertex)
            if result:
                point = result[0].snappedVertex
                self.snapmarker.setCenter(point)
                self.snapmarker.show()
                point = self.toLayerCoordinates(layer,point)
            else:
                point = self.toLayerCoordinates(layer, event.pos())
        else:
            point = self.toLayerCoordinates(layer, event.pos())

        pnt = self.toMapCoordinates(layer, point)
        return pnt

    def canvasMoveEvent(self, event):
        layer = self.canvas.currentLayer()
        if not layer:
            return
        self.getSnapPoint(event,layer)

    def canvasReleaseEvent(self, event):
        if self.count == 2:
            reply = QMessageBox.question(None, "Question", "Move?", QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.move_features()

            self.rb.reset()
            self.rb = None
            self.set_rb()
            self.count = 0
            self.startmarker.hide()
            self.canvas.refresh()


    def set_rb(self):
        self.rb = QgsRubberBand(self.canvas)
        self.rb.setColor(QColor(255, 0, 0, 150))
        self.rb.setWidth(2)

    def check_crs(self):
        layer = self.canvas.currentLayer()
        renderer = self.canvas.mapSettings()
        self.layerCRSSrsid = layer.crs().srsid()
        self.projectCRSSrsid = renderer.destinationCrs().srsid()


    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)
        self.snapmarker = QgsVertexMarker(self.canvas)
        self.snapmarker.setIconType(QgsVertexMarker.ICON_BOX)
        self.snapmarker.setColor(QColor(255,0,0))
        self.snapmarker.setPenWidth(2)
        self.snapmarker.setIconSize(10)
        self.snapmarker.hide()
        self.startmarker = QgsVertexMarker(self.canvas)
        self.startmarker.setIconType(QgsVertexMarker.ICON_BOX)
        self.startmarker.hide()
        self.set_rb()
        self.count = 0

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

    def log(self,msg):
        QgsMessageLog.logMessage(msg, 'MyPlugin',QgsMessageLog.INFO)

