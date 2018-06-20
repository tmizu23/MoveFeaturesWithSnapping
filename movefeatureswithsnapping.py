# -*- coding: utf-8 -*-

# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

#Import own classes and tools
from movefeatureswithsnappingtool import MoveFeaturesWithSnappingTool

# initialize Qt resources from file resources.py
import resources


class MoveFeaturesWithSnapping:

    def __init__(self, iface):
      # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.active = False

    def initGui(self):
        settings = QSettings()
        # Create action
        self.move_features = \
            QAction(QIcon(":/plugins/MoveFeaturesWithSnapping/icon.png"),
                    "MoveFeaturesWithSnapping", self.iface.mainWindow())
        self.move_features.setEnabled(False)
        self.move_features.setCheckable(True)
        # Add toolbar button and menu item
        self.iface.digitizeToolBar().addAction(self.move_features)
        self.iface.editMenu().addAction(self.move_features)

        # Connect to signals for button behaviour
        self.move_features.activated.connect(self.movefeatures)
        self.iface.currentLayerChanged['QgsMapLayer*'].connect(self.toggle)
        self.canvas.mapToolSet['QgsMapTool*'].connect(self.deactivate)

        # Get the tool
        self.tool = MoveFeaturesWithSnappingTool(self.canvas,self.iface)

    def movefeatures(self):
        self.canvas.setMapTool(self.tool)
        self.move_features.setChecked(True)
        self.active = True

    def toggle(self):
        mc = self.canvas
        layer = mc.currentLayer()
        if layer is None:
            return

        #Decide whether the plugin button/menu is enabled or disabled
        if layer.isEditable():
            self.move_features.setEnabled(True)
            try:  # remove any existing connection first
                layer.editingStopped.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
            layer.editingStopped.connect(self.toggle)
            try:
                layer.editingStarted.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
        else:
            self.move_features.setEnabled(False)
            try:  # remove any existing connection first
                layer.editingStarted.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass
            layer.editingStarted.connect(self.toggle)
            try:
                layer.editingStopped.disconnect(self.toggle)
            except TypeError:  # missing connection
                pass


    def deactivate(self):
        self.move_features.setChecked(False)
        self.active = False

    def unload(self):
        self.iface.digitizeToolBar().removeAction(self.move_features)