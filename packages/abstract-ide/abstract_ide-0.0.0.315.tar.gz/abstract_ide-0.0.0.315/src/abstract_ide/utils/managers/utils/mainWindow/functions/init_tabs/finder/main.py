from .FinderWindow import FinderWindow,QApplication,sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FinderWindow()
    window.show()
    sys.exit(app.exec_())
