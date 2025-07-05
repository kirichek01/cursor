from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtCore import QUrl

class TradingView(QWidget):
    """
    The view for the "TradingView" tab.
    It embeds a TradingView chart using QWebEngineView for real-time market analysis.
    This fulfills the requirement for an integrated web chart from the technical specification.
    [cite: uploaded:CombineTradeBot/README.md]
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Sets up the web view and its layout."""
        main_layout = QVBoxLayout(self)
        # Set margins to 0 to make the web view fill the entire tab space
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Using a unique profile for each web view can prevent cookie conflicts
        # and improve stability.
        profile = QWebEngineProfile(self)
        
        self.web_view = QWebEngineView(profile)
        main_layout.addWidget(self.web_view)
        
        # Load the TradingView chart URL.
        # Using the "dark" theme parameter for better integration with our app's style.
        chart_url = QUrl("https://www.tradingview.com/chart/?theme=dark")
        self.web_view.setUrl(chart_url)

