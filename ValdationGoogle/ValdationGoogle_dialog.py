# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ValdationGoogleDialog
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
import resources
import os

from PyQt4 import QtGui, uic
from qgis.core import *
from qgis.gui import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ValdationGoogle_dialog_base.ui'))


class ValdationGoogleDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ValdationGoogleDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
    def closeEvent(self, event):
      print("X is clicked")
      project = QgsProject.instance()
      project.clear()