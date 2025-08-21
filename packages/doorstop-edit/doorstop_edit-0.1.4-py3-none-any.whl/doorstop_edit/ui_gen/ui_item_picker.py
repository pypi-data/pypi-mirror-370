# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'item_picker.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QLineEdit, QListWidget, QListWidgetItem,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ItemPickerDialog(object):
    def setupUi(self, ItemPickerDialog):
        if not ItemPickerDialog.objectName():
            ItemPickerDialog.setObjectName(u"ItemPickerDialog")
        ItemPickerDialog.resize(381, 289)
        self.verticalLayout_2 = QVBoxLayout(ItemPickerDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.search = QLineEdit(ItemPickerDialog)
        self.search.setObjectName(u"search")

        self.verticalLayout.addWidget(self.search)

        self.search_result = QListWidget(ItemPickerDialog)
        self.search_result.setObjectName(u"search_result")
        self.search_result.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout.addWidget(self.search_result)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttons = QDialogButtonBox(ItemPickerDialog)
        self.buttons.setObjectName(u"buttons")
        self.buttons.setOrientation(Qt.Horizontal)
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttons)


        self.retranslateUi(ItemPickerDialog)
        self.buttons.accepted.connect(ItemPickerDialog.accept)
        self.buttons.rejected.connect(ItemPickerDialog.reject)

        QMetaObject.connectSlotsByName(ItemPickerDialog)
    # setupUi

    def retranslateUi(self, ItemPickerDialog):
        ItemPickerDialog.setWindowTitle(QCoreApplication.translate("ItemPickerDialog", u"Item picker", None))
        self.search.setPlaceholderText(QCoreApplication.translate("ItemPickerDialog", u"Search...", None))
    # retranslateUi

