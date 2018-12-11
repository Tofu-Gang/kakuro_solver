__author__ = "Tofu Gang"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from src.mainWindow import MainWindow
import sys



################################################################################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("TofuGangSW")
    QCoreApplication.setApplicationName("Kakuro_solver")
    window = MainWindow()
    window.show()
    app.exec_()
    sys.exit()

################################################################################