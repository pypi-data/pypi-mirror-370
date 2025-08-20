#! /bin/env python
"""
A PyQt5 application to show the web application for launching live editors.
Live editors are launched in the native browser.
"""

import sys
import os
import webbrowser
import logging
import threading
import requests
try:
    from PyQt5 import QtCore, QtGui
    from PyQt5 import QtWidgets as qtw
    from PyQt5 import QtWebEngineWidgets as qwe
except ImportError:
    print("Cannot launch the editor as PyQt5 and/or its web engine are "
          "unavailable. If you installed GitBuilding with pip try running\n\n"
          "    pip install gitbuilding[gui]\n\n"
          "and then tying to run the GUI again.")
    sys.exit(-1)
from gitbuilding import server
from gitbuilding.handler import GBHandler

def gb_icon():
    """
    Helper function that returns the GitBuilding logo as a QIcon
    """
    gb_dir = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(gb_dir, 'static', 'Logo', 'GitBuilding.svg')
    return QtGui.QIcon(icon_path)

class GBWebView(qwe.QWebEngineView):
    """
    A web engine view. Doesn't allow new windows or tabs. Modifies the context
    menu, and starts a spell checker.
    """

    def load(self, url):
        '''
        Loads the input URL into the web view.
        '''
        self.setUrl(QtCore.QUrl(url))

    def createWindow(self, window_type): # pylint: disable=invalid-name
        """
        Override window creation
        """
        if window_type == qwe.QWebEnginePage.WebBrowserWindow:
            dummy_view = qwe.QWebEngineView(self)
            dummy_view.urlChanged.connect(self.capture_dummy_url_window)
            return dummy_view
        if window_type == qwe.QWebEnginePage.WebBrowserTab:
            dummy_view = qwe.QWebEngineView(self)
            dummy_view.urlChanged.connect(self.capture_dummy_url_tab)
            return dummy_view
        return None

    @QtCore.pyqtSlot(QtCore.QUrl)
    def capture_dummy_url_tab(self, url):
        """
        This will capture the url from a dummy window that was created
        and never shown. The tab is then opened externally. See also
        capture_dummy_url_window
        """
        dummy_view = self.sender()
        webbrowser.open_new_tab(url.url())
        dummy_view.deleteLater()

    @QtCore.pyqtSlot(QtCore.QUrl)
    def capture_dummy_url_window(self, url):
        """
        This will capture the url from a dummy window that was created
        and never shown. The broweser window is then opened externally.
        See also capture_dummy_url_tab
        """
        dummy_view = self.sender()
        webbrowser.open_new(url.url())
        dummy_view.deleteLater()

    def change_language(self, lang):
        """
        Changes the laguage of the spell checker.
        """
        profile = self.page().profile()
        profile.setSpellCheckLanguages((lang,))

class WebViewWidget(qtw.QWidget):
    """
    A widget ffor holding the web view
    """

    def __init__(self):
        self.webview = None
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initalises the webview and loads it into the layout
        """
        layout = qtw.QVBoxLayout(self)
        self.webview = GBWebView()
        self.webview.load("http://localhost:6178")
        layout.addWidget(self.webview)


class GBMainWindow(qtw.QWidget):
    """
    Main Window of the GitBuilding application
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Intialise the layout of the main window
        """
        self.setMinimumSize(1000, 600)
        self.setWindowTitle('GitBuilding')
        self.setWindowIcon(gb_icon())

        self.web_widget = WebViewWidget()


        layout = qtw.QVBoxLayout(self)
        layout.addWidget(self.web_widget)

    def closeEvent(self, event): # pylint: disable=invalid-name
        """
        Override the close Event to check if the prgram should be closed.
        Thes doesn't check if the page wants to close, it jsut always warns.
        It is possible to trigger the page action with RequestClose but this
        I have not found a way to wait for the response.
        """
        msg = "Are you sure you want to quit? Any unsaved work will be lost."
        reply = qtw.QMessageBox.question(self, "Message",
                                         msg,
                                         qtw.QMessageBox.Close | qtw.QMessageBox.Cancel,
                                         qtw.QMessageBox.Close)

        if reply == qtw.QMessageBox.Close:
            event.accept()
        else:
            event.ignore()


def run_server(handler):
    """
    Function to start the server this is run in a new thread
    """
    gbs = server.GBServer(handler, os.path.abspath('.'))
    gbs.run(use_waitress=True)

def main():
    """
    Main GUI program, this needs to me merged into the main GitBuilding program
    """
    handler = GBHandler()
    logger = logging.getLogger('BuildUp')
    logger.addHandler(handler)
    #gb_dir = os.path.dirname(os.path.realpath(__file__))
    #dict_dir = os.path.join(gb_dir, "qtwebengine_dictionaries")
    #os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = dict_dir
    app = qtw.QApplication(sys.argv)
    main_window = GBMainWindow()

    t_server = threading.Thread(name='Server',
                                target=run_server,
                                args=(handler,),
                                daemon=True)
    t_server.start()
    server_running = False
    while not server_running:
        try:
            requests.get('http://localhost:6178', timeout=5)
            server_running = True
        except requests.exceptions.ConnectionError:
            pass
    main_window.show()
    app.exec_()

if __name__ == "__main__":
    main()
