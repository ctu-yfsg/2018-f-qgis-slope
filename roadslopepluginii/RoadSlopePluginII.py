# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RoadSlopePluginII
                                 A QGIS plugin
 This plugin compute slope in percent for each line in the vector layer from DEM and split feature with more than two vertex into separate features by changing slope.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-06-16
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Michaela Patakova
        email                : patakovamichala@gmail.com
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
from qgis.core import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.utils import *
from PyQt5.QtGui import QAction, QIcon, QFileDialog
from .RoadSlopePluginII_dialog import RoadSlopePluginIIDialog
import os.path
import math
import os


class RoadSlopePluginII:
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
            'RoadSlopePluginII_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = RoadSlopePluginIIDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RoadSlopePluginII')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RoadSlopePluginII')
        self.toolbar.setObjectName(u'RoadSlopePluginII')

        # clear the previously loaded text (if any) in the line edit widget
        self.dlg.lineEdit.clear()
        # connect the select_output_file method to the clicked signal of the tool button widget
        self.dlg.toolButton.clicked.connect(self.select_output_dir)

        # clear the previously loaded value (if any) in the spin box widget
        self.dlg.spinBox.clear()

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
        return QCoreApplication.translate('RoadSlopePluginII', message)

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

        icon_path = ':/plugins/RoadSlopePluginII/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Road slope plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&RoadSlopePluginII'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_output_dir(self):
        self.dirname = QFileDialog.getExistingDirectory(self.dlg, "Select directory ", "/home")
        self.dlg.lineEdit.setText(self.dirname)

    def run(self):
        """Run method that performs all the real work"""

        # populate the Combo Box with the layers loaded in QGIS
        self.dlg.comboBox.clear()
        self.populateComboBoxes()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            lenghtOfSegment = int(self.dlg.spinBox.value())
            rastCurrentIndex = self.dlg.comboBox.currentIndex()
            vectCurrentIndex = self.dlg.comboBox_2.currentIndex()
            raster = self.dlg.comboBox.itemData(rastCurrentIndex)
            vector = self.dlg.comboBox_2.itemData(vectCurrentIndex)

            #QgsMessageLog.logMessage(str(vector))

            self.processLayer(vector, raster, lenghtOfSegment)
            # QgsMessageLog.logMessage(str(lenghtOfSegment))
            # QgsMessageLog.logMessage(str(raster))

            pass

    def populateComboBoxes(self):
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]

        for layer in layers:
            layerType = layer.type()
            if layerType == QgsMapLayer.VectorLayer:
                self.dlg.comboBox_2.addItem(layer.name(), layer)
            elif layerType == QgsMapLayer.RasterLayer:
                self.dlg.comboBox.addItem(layer.name(), layer)

    def processLayer(self, features, raster, lenghtOfSegment=20):
        # 1. interpolate points along the feature layer

        fields = features.fields()
        fields.append(QgsField('distance', QVariant.Double))
        fields.append(QgsField('angle', QVariant.Double))
        fields.append(QgsField('elevation', QVariant.Double))
        crs = 5514
        spatRef = QgsCoordinateReferenceSystem(crs, QgsCoordinateReferenceSystem.EpsgCrsId)
        filename = r"C:\Users\patmic\Desktop\CVZ_CVUT\Free_software_gis\output\my_shapes2.shp"
        # overwrite output file
        if os.path.exists(filename):
            os.remove(filename)
        else:
            QgsMessageLog.logMessage("Sorry, I can not remove file.")

        writer = QgsVectorFileWriter(
            filename,
            "utf-8",
            fields,
            QgsWkbTypes.Point,
            spatRef,
            "ESRI Shapefile"
        )

        if writer.hasError() != QgsVectorFileWriter.NoError:
            QgsMessageLog.logMessage("Error when creating shapefile: " + writer.errorMessage())

        self.interpolate(features, lenghtOfSegment, writer, raster)

        del writer
        QgsMessageLog.logMessage("writer flushed")

        # 2. intersect output points with raster layer, output is list of elevation values
        # 3. find local extremes and calculate slopes between neighbour extremes
        # 4. create new features where starting point is either local maximum or minimum and endpoint is the other one
        #    than a starting point, where each feature has calculated slope information

    def interpolate(self, layer, length_of_segment, writer, rasterLayer):
        distance = length_of_segment
        start_offset = 0
        end_offset = 0

        features = layer.getFeatures()
        for current, input_feature in enumerate(features):
            input_geometry = input_feature.geometry()
            if not input_geometry:
                writer.addFeature(input_feature)
                #QgsMessageLog.logMessage("adding feature to writer")
            else:
                if input_geometry.type == QgsWkbTypes.PolygonGeometry:
                    length = input_geometry.geometry().perimeter()
                else:
                    length = input_geometry.length() - end_offset
                current_distance = start_offset

                while current_distance <= length:
                    point = input_geometry.interpolate(current_distance)
                    angle = math.degrees(input_geometry.interpolateAngle(current_distance))

                    output_feature = QgsFeature()
                    output_feature.setGeometry(point)
                    attrs = input_feature.attributes()
                    attrs.append(current_distance)
                    attrs.append(angle)
                    attrs.append(getElevation(rasterLayer, point.asPoint()))
                    output_feature.setAttributes(attrs)
                    writer.addFeature(output_feature)
                    #QgsMessageLog.logMessage("adding feature to writer")

                    current_distance += distance



def getElevation(rasterLayer, point):
    band = 1
    results = rasterLayer.dataProvider().identify(point,QgsRaster.IdentifyFormatValue).results()
    return results[band]