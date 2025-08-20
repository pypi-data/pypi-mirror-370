import sys
import warnings
from PyQt5.QtWidgets import QApplication
from ui_main_controller import *
warnings.filterwarnings("ignore")


if __name__=='__main__':
    app = QApplication(sys.argv)

    ui = UI_Main_Controller()
    ui.show()

    sys.exit(app.exec_())