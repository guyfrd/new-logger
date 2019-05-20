import sys
import os
from PySide2.QtWidgets import QApplication
print(sys.path)
sys.path.append(os.path.join('new-log', 'GUI', 'view', 'mainWindow'))
from view.mainWindow import MainWindow



app = QApplication(sys.argv)

window = MainWindow()
window.show()
sys.exit(app.exec_())