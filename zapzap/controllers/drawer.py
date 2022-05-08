from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPropertyAnimation, QAbstractAnimation
from PyQt6 import uic
from zapzap.controllers.settings import Settings
from zapzap import abs_path


class Drawer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(abs_path+'/view/drawer.ui', self)
        self._maximum_width = parent.width()
        self.parent = parent
        self.isOpen = True

        self._animation = QPropertyAnimation(self, b"width")
        self._animation.setStartValue(12)
        self._animation.setDuration(500)
        self._animation.valueChanged.connect(self.setFixedWidth)
        self.show()
        self.blur.hide()

        self.settings = Settings(self)

        self.layoutSettings.addWidget(self.settings)
        
        self.openDrawerButton.clicked.connect(self.onToggled)

        self.frame_drawer.setStyleSheet(
            """QFrame#frame_drawer {border: 5px solid rgba(100, 100, 100, 0.8);border-radius: 10px;}""")

        self.blur.setStyleSheet("""QWidget#blur{
                                    background-color: rgba(0, 0, 0, 0.5);
                                    border-radius: 0px;
                                }""")

        self.openDrawerButton.setStyleSheet("""QPushButton#openDrawerButton
                                {
                                    background-color:  rgba(100, 100, 100, 0.8);
                                    border: 0.01em solid rgba(100, 100, 100, 0.8);
                                    border-radius: 0.09em;
                                }""")

    def onToggled(self):
        if self.isOpen:
            self.open()
            self.isOpen = False
            self.blur.show()
            self.openDrawerButton.hide()
        else:
            self.close()
            self.isOpen = True
            self.blur.hide()
            self.openDrawerButton.show()

    @property
    def maximum_width(self):
        return self._maximum_width

    @maximum_width.setter
    def maximum_width(self, w):
        self._maximum_width = w
        self._animation.setEndValue(self.maximum_width)

    def open(self):
        self._animation.setDuration(100)
        self._animation.setDirection(QAbstractAnimation.Direction.Forward)
        self._animation.start()
        self.show()

    def close(self):
        self._animation.setDuration(100)
        self._animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._animation.start()

    def mousePressEvent(self, event):
        if self.isOpen == False:
            self.onToggled()
