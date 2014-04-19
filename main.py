# -*- coding: utf-8 -*-
__author__ = "Jakub Franěk"

from PySide.QtGui import QApplication
from PySide.QtCore import QCoreApplication
from mainWindow import MainWindow
import sys

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName(u'Másnapos')
    QCoreApplication.setOrganizationDomain('másnapos.hu')
    QCoreApplication.setApplicationName('Kakuro_solver')
    window = MainWindow()
    window.show()
    app.exec_()
    sys.exit()

################################################################################