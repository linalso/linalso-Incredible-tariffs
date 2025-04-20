from PyQt5.QtWidgets import QApplication
import sys
from ui_components import TariffSimulator

def main():
    app = QApplication(sys.argv)
    window = TariffSimulator()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()