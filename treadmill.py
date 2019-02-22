from src.interface import *

def main():
    app = QApplication([])
    gui = MainWindow()
    gui.show()
    app.exec_()


if __name__ == "__main__":
    main()
    