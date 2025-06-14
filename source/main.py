# main.py

import sys
from PyQt5.QtWidgets import QApplication
from gui import OtamatoneGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = OtamatoneGUI()
    gui.show()
    sys.exit(app.exec_())
