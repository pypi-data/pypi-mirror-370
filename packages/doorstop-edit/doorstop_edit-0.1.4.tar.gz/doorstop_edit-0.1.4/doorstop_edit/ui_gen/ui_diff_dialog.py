# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'diff_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QTextBrowser, QToolButton,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_diff_dialog(object):
    def setupUi(self, diff_dialog):
        if not diff_dialog.objectName():
            diff_dialog.setObjectName(u"diff_dialog")
        diff_dialog.resize(715, 460)
        self.verticalLayout = QVBoxLayout(diff_dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(diff_dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.simple_mode_button = QPushButton(self.frame)
        self.simple_mode_button.setObjectName(u"simple_mode_button")
        self.simple_mode_button.setCheckable(True)

        self.horizontalLayout.addWidget(self.simple_mode_button)

        self.git_mode_button = QPushButton(self.frame)
        self.git_mode_button.setObjectName(u"git_mode_button")
        self.git_mode_button.setCheckable(True)

        self.horizontalLayout.addWidget(self.git_mode_button)


        self.verticalLayout.addWidget(self.frame)

        self.description = QLabel(diff_dialog)
        self.description.setObjectName(u"description")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.description.sizePolicy().hasHeightForWidth())
        self.description.setSizePolicy(sizePolicy)
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)

        self.verticalLayout.addWidget(self.description)

        self.vcs_frame = QFrame(diff_dialog)
        self.vcs_frame.setObjectName(u"vcs_frame")
        self.vcs_frame.setFrameShape(QFrame.StyledPanel)
        self.vcs_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.vcs_frame)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.vcs_backward_button = QToolButton(self.vcs_frame)
        self.vcs_backward_button.setObjectName(u"vcs_backward_button")
        icon = QIcon()
        icon.addFile(u":/icons/arrow-left", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.vcs_backward_button.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.vcs_backward_button)

        self.vcs_current_diff_label = QLabel(self.vcs_frame)
        self.vcs_current_diff_label.setObjectName(u"vcs_current_diff_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.vcs_current_diff_label.sizePolicy().hasHeightForWidth())
        self.vcs_current_diff_label.setSizePolicy(sizePolicy1)
        self.vcs_current_diff_label.setMinimumSize(QSize(120, 0))
        self.vcs_current_diff_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.vcs_current_diff_label)

        self.vcs_forward_button = QToolButton(self.vcs_frame)
        self.vcs_forward_button.setObjectName(u"vcs_forward_button")
        icon1 = QIcon()
        icon1.addFile(u":/icons/arrow-right", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.vcs_forward_button.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.vcs_forward_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.label = QLabel(self.vcs_frame)
        self.label.setObjectName(u"label")
        self.label.setMargin(2)

        self.horizontalLayout_3.addWidget(self.label)

        self.horizontalSpacer_4 = QSpacerItem(2, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.vcs_author = QLabel(self.vcs_frame)
        self.vcs_author.setObjectName(u"vcs_author")
        self.vcs_author.setMinimumSize(QSize(200, 0))
        self.vcs_author.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.vcs_author)

        self.label_2 = QLabel(self.vcs_frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMargin(2)

        self.horizontalLayout_3.addWidget(self.label_2)

        self.horizontalSpacer_5 = QSpacerItem(2, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_5)

        self.vcs_date = QLabel(self.vcs_frame)
        self.vcs_date.setObjectName(u"vcs_date")
        self.vcs_date.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_3.addWidget(self.vcs_date)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addWidget(self.vcs_frame)

        self.diff_dialog_text = QTextBrowser(diff_dialog)
        self.diff_dialog_text.setObjectName(u"diff_dialog_text")

        self.verticalLayout.addWidget(self.diff_dialog_text)

        self.diff_dialog_buttons = QDialogButtonBox(diff_dialog)
        self.diff_dialog_buttons.setObjectName(u"diff_dialog_buttons")
        self.diff_dialog_buttons.setOrientation(Qt.Horizontal)
        self.diff_dialog_buttons.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout.addWidget(self.diff_dialog_buttons)


        self.retranslateUi(diff_dialog)
        self.diff_dialog_buttons.accepted.connect(diff_dialog.accept)
        self.diff_dialog_buttons.rejected.connect(diff_dialog.reject)

        QMetaObject.connectSlotsByName(diff_dialog)
    # setupUi

    def retranslateUi(self, diff_dialog):
        diff_dialog.setWindowTitle(QCoreApplication.translate("diff_dialog", u"Diff", None))
        self.simple_mode_button.setText(QCoreApplication.translate("diff_dialog", u"Simple", None))
        self.git_mode_button.setText(QCoreApplication.translate("diff_dialog", u"Git", None))
        self.description.setText(QCoreApplication.translate("diff_dialog", u"<html><head/><body><p><br/></p></body></html>", None))
        self.vcs_backward_button.setText(QCoreApplication.translate("diff_dialog", u"...", None))
        self.vcs_current_diff_label.setText(QCoreApplication.translate("diff_dialog", u"1/23", None))
        self.vcs_forward_button.setText(QCoreApplication.translate("diff_dialog", u"...", None))
        self.label.setText(QCoreApplication.translate("diff_dialog", u"<html><head/><body><p><span style=\" font-weight:700;\">Author:</span></p></body></html>", None))
        self.vcs_author.setText(QCoreApplication.translate("diff_dialog", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate("diff_dialog", u"<html><head/><body><p><span style=\" font-weight:700;\">Date:</span></p></body></html>", None))
        self.vcs_date.setText(QCoreApplication.translate("diff_dialog", u"TextLabel", None))
    # retranslateUi

