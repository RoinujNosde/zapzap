from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon
from PyQt6.QtGui import QMoveEvent
from PyQt6.QtCore import QSettings, QByteArray, QTimer
from PyQt6 import uic
import zapzap
from zapzap.assets.themes.dark.stylesheet import STYLE_SHEET_DARK
from zapzap.assets.themes.light.stylesheet import STYLE_SHEET_LIGHT
from zapzap.controllers.about import About
from zapzap.controllers.main_window_components.menu_bar import MenuBar
from zapzap.controllers.main_window_components.tray_icon import TrayIcon
from zapzap.controllers.settings import Settings
from zapzap.controllers.settings_new import SettingsNew
from zapzap.engine.browser import Browser
from zapzap import theme_light_path, theme_dark_path
from zapzap.services.dbus_theme import get_system_theme


class MainWindow(QMainWindow):

    openDialog = None
    isFullScreen = False
    isHideMenuBar = False
    list_browser = []  # remover isso depois
    container_list = []

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        uic.loadUi(zapzap.abs_path+'/view/main_window.ui', self)
        self.app = parent
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)

        MenuBar(self)
        self.tray = TrayIcon(self)

        self.createWebEngine()

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()
        self.current_theme = -1

        #self.openSettingsDialog()

    def recurring_timer(self):
        theme = get_system_theme()
        if self.current_theme != theme:
            self.current_theme = theme
            self.browser.whats.setTheme(self.current_theme)
            self.setThemeApp(self.current_theme)

    def createWebEngine(self):
        self.browser = Browser(self)
        self.browser.setZoomFactor(self.settings.value(
            "browser/zoomFactor", 1.0, float))
        self.browser.doReload()
        self.stackedWidget.insertWidget(0, self.browser)

    def setNight_mode(self):
        print('desativado')
        # isNight_mode = not self.settings.value(
        #    "system/night_mode", False, bool)
        # self.browser.whats.setTheme(isNight_mode)
        # self.setThemeApp(isNight_mode)

        #self.settings.setValue("system/night_mode", isNight_mode)

    def setThemeApp(self, isNight_mode):
        stylesheet = None
        if isNight_mode:
            #path = theme_dark_path
            #palete = PALETTE_DARK
            stylesheet = STYLE_SHEET_DARK
        else:
            #path = theme_light_path
            #palete = PALETTE_LIGHT
            stylesheet = STYLE_SHEET_LIGHT
        # with open(path, 'r') as f:
        #    style = f.read()
        self.app.setStyleSheet(stylesheet)
        # Set the stylesheet of the application
        # self.app.setStyleSheet(style)

    def reload_Service(self):
        self.browser.doReload()

    def setDefault_size_page(self):
        self.browser.setZoomFactor(1.0)

    def openSettingsDialog(self):
        #self.openDialog = Settings()
        # self.openDialog.show()
        self.stackedWidget.insertWidget(1, SettingsNew(self))
        self.stackedWidget.setCurrentIndex(1)

    def openAbout_Zapzap(self):
        self.openDialog = About(self)
        self.openDialog.show()

    def moveEvent(self, a0: QMoveEvent) -> None:
        if self.openDialog != None:
            self.openDialog.centerPos()
        return super().moveEvent(a0)

    def loadSettings(self):
        """
        Load the settings
        """
        # Theme App
        #self.setThemeApp(self.settings.value("system/night_mode", False, bool))
        self.setThemeApp(get_system_theme())  # pega o do sistema
        # MenuBar
        self.isHideMenuBar = self.settings.value(
            "main/hideMenuBar", False, bool)
        self.setHideMenuBar()
        # keep_background
        self.actionHide_on_close.setChecked(self.settings.value(
            "system/keep_background", True, bool))
        # Window State
        self.restoreGeometry(self.settings.value(
            "main/geometry", QByteArray()))
        self.restoreState(self.settings.value(
            "main/windowState", QByteArray()))
        # System start
        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        isStart_hide = self.settings.value("system/start_hide", False, bool)
        if isStart_system and isStart_hide:
            self.hide()
        else:
            self.show()

    def quit(self):
        """
        Close window.
        """
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.hide()
        self.app.quit()

    def closeEvent(self, event):
        """
        Override the window close event.
        Save window dimensions and check if it should be hidden or closed
        """
        self.settings.setValue("browser/zoomFactor", self.browser.zoomFactor())
        self.settings.setValue("main/geometry", self.saveGeometry())
        self.settings.setValue("main/windowState", self.saveState())
        self.timer.stop()
        if self.settings.value(
                "system/keep_background", True, bool):
            self.hide()
            event.ignore()

    def onTrayIconActivated(self, reason):
        """
        wind to show and hide the window with just two click or middle button on the tray icon. 
        One click opens the menu.
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.on_show()
            self.app.activateWindow()

    def on_show(self):
        """
        Opening the system tray web app.
        """
        self.loadSettings()
        self.timer.start()
        if self.app.activeWindow() != None:  # Se a janela estiver em foco será escondida
            self.hide()
        else:  # Caso não esteja, será mostrada
            self.show()
            self.app.activateWindow()

    def setFullSreen(self):
        """
        Full Screen Window
        """
        if not self.isFullScreen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.isFullScreen = not self.isFullScreen

    def setHideMenuBar(self):
        """
        Hide/Show MenuBar
        """
        if self.isHideMenuBar:
            self.menubar.setMaximumHeight(0)
        else:
            # default size for qt designer
            self.menubar.setMaximumHeight(16777215)

        self.settings.setValue("main/hideMenuBar", self.isHideMenuBar)
        self.isHideMenuBar = not self.isHideMenuBar
