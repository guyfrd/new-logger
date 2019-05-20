import sys
from PySide2.QtWidgets import QApplication
from GUI.view.mainWindow import MainWindow

app = QApplication(sys.argv)

window = MainWindow()
window.show()
sys.exit(app.exec_())