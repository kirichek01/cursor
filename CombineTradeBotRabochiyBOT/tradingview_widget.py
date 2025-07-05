from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl
_HTML = '<html><body style="margin:0"><h3 style="color:#ccc;text-align:center">TradingView Placeholder</h3></body></html>'
class TradingViewWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHtml(_HTML, QUrl('about:blank'))
