# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'item_viewer.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget)

class Ui_ItemViewer(object):
    def setupUi(self, ItemViewer):
        if not ItemViewer.objectName():
            ItemViewer.setObjectName(u"ItemViewer")
        ItemViewer.resize(892, 844)
        self.verticalLayout = QVBoxLayout(ItemViewer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.web_engine_view = QWebEngineView(ItemViewer)
        self.web_engine_view.setObjectName(u"web_engine_view")
        self.web_engine_view.setMaximumSize(QSize(800, 16777215))
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(240, 240, 240, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush1)
        brush2 = QBrush(QColor(130, 130, 130, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush2)
        self.web_engine_view.setPalette(palette)

        self.horizontalLayout.addWidget(self.web_engine_view)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(ItemViewer)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ItemViewer)
        self.buttonBox.accepted.connect(ItemViewer.accept)
        self.buttonBox.rejected.connect(ItemViewer.reject)

        QMetaObject.connectSlotsByName(ItemViewer)
    # setupUi

    def retranslateUi(self, ItemViewer):
        ItemViewer.setWindowTitle(QCoreApplication.translate("ItemViewer", u"Item Viewer", None))
    # retranslateUi

