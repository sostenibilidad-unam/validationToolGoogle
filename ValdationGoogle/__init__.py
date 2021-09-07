# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ValdationGoogle
                                 A QGIS plugin
 ValdationGoogle
                             -------------------
        begin                : 2016-12-08
        copyright            : (C) 2016 by Fidel Serrano/LANCIS
        email                : serranoycandela@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ValdationGoogle class from file ValdationGoogle.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ValdationGoogle import ValdationGoogle
    return ValdationGoogle(iface)
