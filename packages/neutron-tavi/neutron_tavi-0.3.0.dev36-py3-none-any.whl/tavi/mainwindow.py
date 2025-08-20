"""Main Qt window"""

from qtpy.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from tavi.help.help_model import help_function

# from tavi.tavi.tavi_model import taviModel
# from tavi.tavi.tavi_presenter import taviPresenter
from tavi.tavi_view.taviView import TaviView


class MainWindow(QWidget):
    """Main widget"""

    def __init__(self, parent=None):
        """Constructor"""
        super().__init__(parent)

        ### Create widgets here ###
        tavi_view = TaviView(self)
        # tavi_model = taviModel()
        # self.tavi_presenter = taviPresenter(tavi_view, tavi_model)

        ### Set the layout
        layout = QVBoxLayout()
        layout.addWidget(tavi_view)

        ### Create bottom interface here ###

        # Help button
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.handle_help)

        # Set bottom interface layout
        hor_layout = QHBoxLayout()
        hor_layout.addWidget(help_button)
        layout.addLayout(hor_layout)

        self.setLayout(layout)

        # register child widgets to make testing easier
        self.tavi_view = tavi_view

    def handle_help(self):
        help_function(context="tavi_View")
