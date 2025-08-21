# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QComboBox, QDockWidget, QFormLayout, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPlainTextEdit, QProgressBar,
    QScrollArea, QSizePolicy, QSpacerItem, QStatusBar,
    QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1768, 948)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/icons/favicon", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.menu_action_exit = QAction(MainWindow)
        self.menu_action_exit.setObjectName(u"menu_action_exit")
        icon1 = QIcon()
        icon1.addFile(u":/icons/exit", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.menu_action_exit.setIcon(icon1)
        self.menu_action_show_item_editor = QAction(MainWindow)
        self.menu_action_show_item_editor.setObjectName(u"menu_action_show_item_editor")
        self.menu_action_show_item_editor.setCheckable(True)
        self.menu_action_show_item_editor.setChecked(True)
        self.menu_action_show_document_tree = QAction(MainWindow)
        self.menu_action_show_document_tree.setObjectName(u"menu_action_show_document_tree")
        self.menu_action_show_document_tree.setCheckable(True)
        self.menu_action_show_document_tree.setChecked(True)
        self.menu_action_show_pinned_items = QAction(MainWindow)
        self.menu_action_show_pinned_items.setObjectName(u"menu_action_show_pinned_items")
        self.menu_action_show_pinned_items.setCheckable(True)
        self.menu_action_show_pinned_items.setChecked(True)
        self.menu_action_about = QAction(MainWindow)
        self.menu_action_about.setObjectName(u"menu_action_about")
        self.menu_action_settings = QAction(MainWindow)
        self.menu_action_settings.setObjectName(u"menu_action_settings")
        self.menu_action_open_folder = QAction(MainWindow)
        self.menu_action_open_folder.setObjectName(u"menu_action_open_folder")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.view_items_widget = QWidget(self.centralwidget)
        self.view_items_widget.setObjectName(u"view_items_widget")
        self.view_items_widget.setMaximumSize(QSize(800, 16777215))
        self.verticalLayout_8 = QVBoxLayout(self.view_items_widget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.view_items_mode = QComboBox(self.view_items_widget)
        self.view_items_mode.addItem("")
        self.view_items_mode.addItem("")
        self.view_items_mode.addItem("")
        self.view_items_mode.setObjectName(u"view_items_mode")
        self.view_items_mode.setMinimumSize(QSize(200, 0))

        self.horizontalLayout_4.addWidget(self.view_items_mode)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.render_progress_bar = QProgressBar(self.view_items_widget)
        self.render_progress_bar.setObjectName(u"render_progress_bar")
        self.render_progress_bar.setMaximumSize(QSize(100, 5))
        self.render_progress_bar.setValue(24)
        self.render_progress_bar.setTextVisible(False)

        self.horizontalLayout_4.addWidget(self.render_progress_bar)


        self.verticalLayout_8.addLayout(self.horizontalLayout_4)

        self.web_engine_view = QWebEngineView(self.view_items_widget)
        self.web_engine_view.setObjectName(u"web_engine_view")
        self.web_engine_view.setMaximumSize(QSize(16777215, 16777215))
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

        self.verticalLayout_8.addWidget(self.web_engine_view)

        self.renderer_search_box = QLineEdit(self.view_items_widget)
        self.renderer_search_box.setObjectName(u"renderer_search_box")

        self.verticalLayout_8.addWidget(self.renderer_search_box)


        self.horizontalLayout.addWidget(self.view_items_widget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1768, 20))
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuAbout = QMenu(self.menubar)
        self.menuAbout.setObjectName(u"menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.edit_item_dock_widget = QDockWidget(MainWindow)
        self.edit_item_dock_widget.setObjectName(u"edit_item_dock_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.edit_item_dock_widget.sizePolicy().hasHeightForWidth())
        self.edit_item_dock_widget.setSizePolicy(sizePolicy1)
        self.edit_item_dock_widget.setMinimumSize(QSize(306, 138))
        self.edit_item_dock_widget.setMaximumSize(QSize(1200, 524287))
        self.edit_item_dock_widget.setBaseSize(QSize(0, 0))
        self.edit_item_dock_widget.setStyleSheet(u"")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.dockWidgetContents_3.setMaximumSize(QSize(1200, 16777215))
        self.verticalLayout = QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.edit_item_tool_bar = QFrame(self.dockWidgetContents_3)
        self.edit_item_tool_bar.setObjectName(u"edit_item_tool_bar")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.edit_item_tool_bar.sizePolicy().hasHeightForWidth())
        self.edit_item_tool_bar.setSizePolicy(sizePolicy2)
        self.edit_item_tool_bar.setMaximumSize(QSize(16777215, 16777215))
        self.edit_item_tool_bar.setFrameShape(QFrame.StyledPanel)
        self.edit_item_tool_bar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.edit_item_tool_bar)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.item_edit_uid = QLineEdit(self.edit_item_tool_bar)
        self.item_edit_uid.setObjectName(u"item_edit_uid")
        self.item_edit_uid.setMinimumSize(QSize(100, 0))
        self.item_edit_uid.setMaximumSize(QSize(400, 16777215))
        self.item_edit_uid.setStyleSheet(u"color: rgb(154, 153, 150);")
        self.item_edit_uid.setReadOnly(True)

        self.horizontalLayout_6.addWidget(self.item_edit_uid)

        self.item_edit_copy_uid_clipboard_button = QToolButton(self.edit_item_tool_bar)
        self.item_edit_copy_uid_clipboard_button.setObjectName(u"item_edit_copy_uid_clipboard_button")
        icon2 = QIcon()
        icon2.addFile(u":/icons/copy", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.item_edit_copy_uid_clipboard_button.setIcon(icon2)

        self.horizontalLayout_6.addWidget(self.item_edit_copy_uid_clipboard_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_2)

        self.edit_item_wrap_text_button = QToolButton(self.edit_item_tool_bar)
        self.edit_item_wrap_text_button.setObjectName(u"edit_item_wrap_text_button")
        icon3 = QIcon()
        icon3.addFile(u":/icons/wrap", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.edit_item_wrap_text_button.setIcon(icon3)
        self.edit_item_wrap_text_button.setCheckable(True)

        self.horizontalLayout_6.addWidget(self.edit_item_wrap_text_button)

        self.item_edit_review_button = QToolButton(self.edit_item_tool_bar)
        self.item_edit_review_button.setObjectName(u"item_edit_review_button")
        icon4 = QIcon()
        icon4.addFile(u":/icons/review-item", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.item_edit_review_button.setIcon(icon4)

        self.horizontalLayout_6.addWidget(self.item_edit_review_button)

        self.item_edit_clear_suspects_button = QToolButton(self.edit_item_tool_bar)
        self.item_edit_clear_suspects_button.setObjectName(u"item_edit_clear_suspects_button")
        icon5 = QIcon()
        icon5.addFile(u":/icons/clear-links", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.item_edit_clear_suspects_button.setIcon(icon5)

        self.horizontalLayout_6.addWidget(self.item_edit_clear_suspects_button)

        self.item_edit_diff_button = QToolButton(self.edit_item_tool_bar)
        self.item_edit_diff_button.setObjectName(u"item_edit_diff_button")
        icon6 = QIcon()
        icon6.addFile(u":/icons/diff", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.item_edit_diff_button.setIcon(icon6)

        self.horizontalLayout_6.addWidget(self.item_edit_diff_button)

        self.item_edit_undo_button = QToolButton(self.edit_item_tool_bar)
        self.item_edit_undo_button.setObjectName(u"item_edit_undo_button")
        icon7 = QIcon()
        icon7.addFile(u":/icons/undo", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.item_edit_undo_button.setIcon(icon7)

        self.horizontalLayout_6.addWidget(self.item_edit_undo_button)


        self.verticalLayout.addWidget(self.edit_item_tool_bar)

        self.scrollArea = QScrollArea(self.dockWidgetContents_3)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QSize(0, 0))
        self.scrollArea.setBaseSize(QSize(0, 0))
        self.scrollArea.setFrameShape(QFrame.StyledPanel)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setEnabled(True)
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 351, 836))
        sizePolicy1.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy1)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SetNoConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.item_edit_group = QFrame(self.scrollAreaWidgetContents)
        self.item_edit_group.setObjectName(u"item_edit_group")
        self.item_edit_group.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_6 = QVBoxLayout(self.item_edit_group)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.item_edit_form_layout = QFormLayout()
        self.item_edit_form_layout.setObjectName(u"item_edit_form_layout")
        self.item_edit_form_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.item_edit_form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.item_edit_form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.item_edit_form_layout.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.item_edit_form_layout.setFormAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.item_edit_form_layout.setHorizontalSpacing(6)
        self.item_edit_form_layout.setVerticalSpacing(2)
        self.item_edit_form_layout.setContentsMargins(4, 4, 4, 4)
        self.item_edit_review_status_label = QLabel(self.item_edit_group)
        self.item_edit_review_status_label.setObjectName(u"item_edit_review_status_label")

        self.item_edit_form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.item_edit_review_status_label)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.item_edit_active_check_box = QCheckBox(self.item_edit_group)
        self.item_edit_active_check_box.setObjectName(u"item_edit_active_check_box")

        self.horizontalLayout_9.addWidget(self.item_edit_active_check_box)

        self.horizontalSpacer_6 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_6)

        self.item_edit_normative_check_box = QCheckBox(self.item_edit_group)
        self.item_edit_normative_check_box.setObjectName(u"item_edit_normative_check_box")

        self.horizontalLayout_9.addWidget(self.item_edit_normative_check_box)

        self.horizontalSpacer_7 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_7)

        self.item_edit_derived_check_box = QCheckBox(self.item_edit_group)
        self.item_edit_derived_check_box.setObjectName(u"item_edit_derived_check_box")

        self.horizontalLayout_9.addWidget(self.item_edit_derived_check_box)


        self.item_edit_form_layout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_9)

        self.levelLabel = QLabel(self.item_edit_group)
        self.levelLabel.setObjectName(u"levelLabel")

        self.item_edit_form_layout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.levelLabel)

        self.item_edit_level_line_edit = QLineEdit(self.item_edit_group)
        self.item_edit_level_line_edit.setObjectName(u"item_edit_level_line_edit")
        self.item_edit_level_line_edit.setMinimumSize(QSize(200, 0))
        self.item_edit_level_line_edit.setMaximumSize(QSize(100, 16777215))

        self.item_edit_form_layout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.item_edit_level_line_edit)

        self.label = QLabel(self.item_edit_group)
        self.label.setObjectName(u"label")

        self.item_edit_form_layout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label)

        self.item_edit_header_line_edit = QLineEdit(self.item_edit_group)
        self.item_edit_header_line_edit.setObjectName(u"item_edit_header_line_edit")
        self.item_edit_header_line_edit.setMinimumSize(QSize(200, 0))
        self.item_edit_header_line_edit.setMaximumSize(QSize(650, 16777215))

        self.item_edit_form_layout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.item_edit_header_line_edit)

        self.label_2 = QLabel(self.item_edit_group)
        self.label_2.setObjectName(u"label_2")

        self.item_edit_form_layout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.widget_3 = QWidget(self.item_edit_group)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_7 = QVBoxLayout(self.widget_3)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.item_edit_text_text_edit = QPlainTextEdit(self.widget_3)
        self.item_edit_text_text_edit.setObjectName(u"item_edit_text_text_edit")
        sizePolicy.setHeightForWidth(self.item_edit_text_text_edit.sizePolicy().hasHeightForWidth())
        self.item_edit_text_text_edit.setSizePolicy(sizePolicy)
        self.item_edit_text_text_edit.setMinimumSize(QSize(200, 300))
        self.item_edit_text_text_edit.setMaximumSize(QSize(650, 900))
        self.item_edit_text_text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.verticalLayout_7.addWidget(self.item_edit_text_text_edit)


        self.item_edit_form_layout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.widget_3)

        self.label_3 = QLabel(self.item_edit_group)
        self.label_3.setObjectName(u"label_3")

        self.item_edit_form_layout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.item_edit_link_list = QListWidget(self.item_edit_group)
        QListWidgetItem(self.item_edit_link_list)
        QListWidgetItem(self.item_edit_link_list)
        QListWidgetItem(self.item_edit_link_list)
        QListWidgetItem(self.item_edit_link_list)
        QListWidgetItem(self.item_edit_link_list)
        QListWidgetItem(self.item_edit_link_list)
        self.item_edit_link_list.setObjectName(u"item_edit_link_list")
        sizePolicy.setHeightForWidth(self.item_edit_link_list.sizePolicy().hasHeightForWidth())
        self.item_edit_link_list.setSizePolicy(sizePolicy)
        self.item_edit_link_list.setMinimumSize(QSize(0, 100))
        self.item_edit_link_list.setMaximumSize(QSize(250, 150))
        self.item_edit_link_list.setFrameShape(QFrame.Panel)
        self.item_edit_link_list.setLineWidth(1)
        self.item_edit_link_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.item_edit_link_list.setAlternatingRowColors(True)

        self.item_edit_form_layout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.item_edit_link_list)

        self.line = QFrame(self.item_edit_group)
        self.line.setObjectName(u"line")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy3)
        self.line.setLineWidth(5)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.item_edit_form_layout.setWidget(11, QFormLayout.ItemRole.SpanningRole, self.line)


        self.verticalLayout_6.addLayout(self.item_edit_form_layout)


        self.verticalLayout_2.addWidget(self.item_edit_group)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.edit_item_dock_widget.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.edit_item_dock_widget)
        self.item_tree_dock_widget = QDockWidget(MainWindow)
        self.item_tree_dock_widget.setObjectName(u"item_tree_dock_widget")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_3 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget_2 = QWidget(self.dockWidgetContents)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_4 = QVBoxLayout(self.widget_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.frame = QFrame(self.widget_2)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tree_combo_box = QComboBox(self.frame)
        self.tree_combo_box.addItem("")
        self.tree_combo_box.addItem("")
        self.tree_combo_box.addItem("")
        self.tree_combo_box.addItem("")
        self.tree_combo_box.setObjectName(u"tree_combo_box")

        self.horizontalLayout_2.addWidget(self.tree_combo_box)

        self.edit_document_button = QToolButton(self.frame)
        self.edit_document_button.setObjectName(u"edit_document_button")
        icon8 = QIcon()
        icon8.addFile(u":/icons/add-document", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.edit_document_button.setIcon(icon8)

        self.horizontalLayout_2.addWidget(self.edit_document_button)

        self.toolButton_2 = QToolButton(self.frame)
        self.toolButton_2.setObjectName(u"toolButton_2")
        icon9 = QIcon()
        icon9.addFile(u":/icons/trash-can", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.toolButton_2.setIcon(icon9)

        self.horizontalLayout_2.addWidget(self.toolButton_2)


        self.verticalLayout_10.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.doc_review_tool_button = QToolButton(self.frame)
        self.doc_review_tool_button.setObjectName(u"doc_review_tool_button")
        icon10 = QIcon()
        icon10.addFile(u":/icons/review-doc", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.doc_review_tool_button.setIcon(icon10)

        self.horizontalLayout_5.addWidget(self.doc_review_tool_button)

        self.doc_clear_links_tool_button = QToolButton(self.frame)
        self.doc_clear_links_tool_button.setObjectName(u"doc_clear_links_tool_button")
        self.doc_clear_links_tool_button.setIcon(icon5)

        self.horizontalLayout_5.addWidget(self.doc_clear_links_tool_button)

        self.doc_reorder_level_tool_button = QToolButton(self.frame)
        self.doc_reorder_level_tool_button.setObjectName(u"doc_reorder_level_tool_button")
        icon11 = QIcon()
        icon11.addFile(u":/icons/level-sort", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.doc_reorder_level_tool_button.setIcon(icon11)

        self.horizontalLayout_5.addWidget(self.doc_reorder_level_tool_button)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)


        self.verticalLayout_10.addLayout(self.horizontalLayout_5)


        self.verticalLayout_4.addWidget(self.frame)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.item_tree_search_input = QLineEdit(self.widget_2)
        self.item_tree_search_input.setObjectName(u"item_tree_search_input")

        self.horizontalLayout_3.addWidget(self.item_tree_search_input)

        self.item_tree_clear_search = QToolButton(self.widget_2)
        self.item_tree_clear_search.setObjectName(u"item_tree_clear_search")
        icon12 = QIcon()
        icon12.addFile(u":/icons/clear-text", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.item_tree_clear_search.setIcon(icon12)

        self.horizontalLayout_3.addWidget(self.item_tree_clear_search)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.item_tree_widget = QTreeWidget(self.widget_2)
        QTreeWidgetItem(self.item_tree_widget)
        __qtreewidgetitem = QTreeWidgetItem(self.item_tree_widget)
        QTreeWidgetItem(__qtreewidgetitem)
        self.item_tree_widget.setObjectName(u"item_tree_widget")
        self.item_tree_widget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.item_tree_widget.setDragEnabled(True)
        self.item_tree_widget.setDefaultDropAction(Qt.MoveAction)
        self.item_tree_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.verticalLayout_4.addWidget(self.item_tree_widget)


        self.verticalLayout_3.addWidget(self.widget_2)

        self.item_tree_dock_widget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.item_tree_dock_widget)
        self.pinned_items_dock_widget = QDockWidget(MainWindow)
        self.pinned_items_dock_widget.setObjectName(u"pinned_items_dock_widget")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.verticalLayout_5 = QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.pinned_items_list = QListWidget(self.dockWidgetContents_2)
        self.pinned_items_list.setObjectName(u"pinned_items_list")
        self.pinned_items_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.verticalLayout_5.addWidget(self.pinned_items_list)

        self.pinned_items_dock_widget.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pinned_items_dock_widget)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.menu_file.addAction(self.menu_action_open_folder)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.menu_action_settings)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.menu_action_exit)
        self.menuView.addAction(self.menu_action_show_document_tree)
        self.menuView.addAction(self.menu_action_show_item_editor)
        self.menuView.addAction(self.menu_action_show_pinned_items)
        self.menuAbout.addAction(self.menu_action_about)

        self.retranslateUi(MainWindow)
        self.item_tree_clear_search.clicked.connect(self.item_tree_search_input.clear)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Doorstop Edit", None))
        self.menu_action_exit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.menu_action_show_item_editor.setText(QCoreApplication.translate("MainWindow", u"Item Editor", None))
        self.menu_action_show_document_tree.setText(QCoreApplication.translate("MainWindow", u"Document Tree", None))
        self.menu_action_show_pinned_items.setText(QCoreApplication.translate("MainWindow", u"Pinned Items", None))
        self.menu_action_about.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.menu_action_settings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.menu_action_settings.setToolTip(QCoreApplication.translate("MainWindow", u"Open settings", None))
#endif // QT_CONFIG(tooltip)
        self.menu_action_open_folder.setText(QCoreApplication.translate("MainWindow", u"Open Folder...", None))
        self.view_items_mode.setItemText(0, QCoreApplication.translate("MainWindow", u"Document", None))
        self.view_items_mode.setItemText(1, QCoreApplication.translate("MainWindow", u"Section", None))
        self.view_items_mode.setItemText(2, QCoreApplication.translate("MainWindow", u"Item", None))

#if QT_CONFIG(tooltip)
        self.view_items_mode.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>View mode.</p><p><span style=\" font-weight:700;\">Document:</span> View whole document.</p><p><span style=\" font-weight:700;\">Section:</span> View section only (does not include children).</p><p><span style=\" font-weight:700;\">Item:</span> Only view item.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.renderer_search_box.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Find in document", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuAbout.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
#if QT_CONFIG(tooltip)
        self.edit_item_dock_widget.setToolTip(QCoreApplication.translate("MainWindow", u"Edit requirement item", None))
#endif // QT_CONFIG(tooltip)
        self.edit_item_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
#if QT_CONFIG(tooltip)
        self.item_edit_uid.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The items unique ID. Is part of filename and cannot be changed in this editor.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.item_edit_copy_uid_clipboard_button.setToolTip(QCoreApplication.translate("MainWindow", u"Copy UID to clipboard", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_copy_uid_clipboard_button.setText(QCoreApplication.translate("MainWindow", u"C", None))
#if QT_CONFIG(tooltip)
        self.edit_item_wrap_text_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Wrap text that do not fit the window. </p><p>Applied to custom text input fields as well. </p><p>This button does not affect the result written to file.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.edit_item_wrap_text_button.setText(QCoreApplication.translate("MainWindow", u"Wrap", None))
#if QT_CONFIG(tooltip)
        self.item_edit_review_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Mark item as reviewed.</p><p>Calculates and stores fingerprint (checksum) of attributes that are part of the fingerprint. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_review_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.item_edit_clear_suspects_button.setToolTip(QCoreApplication.translate("MainWindow", u"Clear all suspect links in this item.", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_clear_suspects_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.item_edit_diff_button.setToolTip(QCoreApplication.translate("MainWindow", u"View changes made to this item since application startup.", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_diff_button.setText(QCoreApplication.translate("MainWindow", u"Diff", None))
#if QT_CONFIG(tooltip)
        self.item_edit_undo_button.setToolTip(QCoreApplication.translate("MainWindow", u"Revert all changes made to this item.", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_undo_button.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
#if QT_CONFIG(tooltip)
        self.item_edit_review_status_label.setToolTip(QCoreApplication.translate("MainWindow", u"Current fingerprint status of item.", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_review_status_label.setText(QCoreApplication.translate("MainWindow", u"NOT REVIWED", None))
#if QT_CONFIG(tooltip)
        self.item_edit_active_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Determines if the item is active or not. </p><p>Only active items are included when the corresponding document is published. Inactive items are excluded from validation.</p><p><span style=\" font-weight:700;\">Not part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_active_check_box.setText(QCoreApplication.translate("MainWindow", u"Active", None))
#if QT_CONFIG(tooltip)
        self.item_edit_normative_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If normative (how to comply) or informative (help with conceptual understanding).</p><p><span style=\" font-weight:700;\">Not part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_normative_check_box.setText(QCoreApplication.translate("MainWindow", u"Normative", None))
#if QT_CONFIG(tooltip)
        self.item_edit_derived_check_box.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Indicates if the item is derived or not.</p><p><span style=\" font-weight:700;\">Not part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.item_edit_derived_check_box.setText(QCoreApplication.translate("MainWindow", u"Derived", None))
#if QT_CONFIG(tooltip)
        self.levelLabel.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Indicates the presentation order within a document. A level of 1.1 will display above level 1.2 and 1.1.5 displays below 1.1.2.</p><p>If the level ends with .0 and the item is non-normative, Doorstop will treat the item as a document heading.</p><p><span style=\" font-weight:700;\">Not part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.levelLabel.setText(QCoreApplication.translate("MainWindow", u"Level", None))
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Gives a header (i.e. title) for the item. It will be printed alongside the item UID when published as HTML and Markdown. Links will also include the header text.</p><p><span style=\" font-weight:700;\">Not part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("MainWindow", u"Header", None))
#if QT_CONFIG(tooltip)
        self.label_2.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Item text. This is the main body of the item. Doorstop treats the value as markdown to support rich text, images and tables.</p><p><span style=\" font-weight:700;\">Part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Text", None))
        self.item_edit_text_text_edit.setPlainText(QCoreApplication.translate("MainWindow", u"Some text.\n"
"\n"
"Blah blah blah", None))
        self.item_edit_text_text_edit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter requirement text here...", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>A list of links to parent item(s). A link indicates a relationship between two items in the document tree.</p><p><span style=\" font-weight:700;\">Part of fingerprint.</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Links", None))

        __sortingEnabled = self.item_edit_link_list.isSortingEnabled()
        self.item_edit_link_list.setSortingEnabled(False)
        ___qlistwidgetitem = self.item_edit_link_list.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("MainWindow", u"SFRS-123", None));
        ___qlistwidgetitem1 = self.item_edit_link_list.item(1)
        ___qlistwidgetitem1.setText(QCoreApplication.translate("MainWindow", u"New Item", None));
        ___qlistwidgetitem2 = self.item_edit_link_list.item(2)
        ___qlistwidgetitem2.setText(QCoreApplication.translate("MainWindow", u"New Item", None));
        ___qlistwidgetitem3 = self.item_edit_link_list.item(3)
        ___qlistwidgetitem3.setText(QCoreApplication.translate("MainWindow", u"FRS-12", None));
        ___qlistwidgetitem4 = self.item_edit_link_list.item(4)
        ___qlistwidgetitem4.setText(QCoreApplication.translate("MainWindow", u"FRS-13", None));
        ___qlistwidgetitem5 = self.item_edit_link_list.item(5)
        ___qlistwidgetitem5.setText(QCoreApplication.translate("MainWindow", u"FRS-14", None));
        self.item_edit_link_list.setSortingEnabled(__sortingEnabled)

        self.item_tree_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Document Tree", None))
        self.tree_combo_box.setItemText(0, QCoreApplication.translate("MainWindow", u"ISO-56-1177", None))
        self.tree_combo_box.setItemText(1, QCoreApplication.translate("MainWindow", u"FRS", None))
        self.tree_combo_box.setItemText(2, QCoreApplication.translate("MainWindow", u"SFRS", None))
        self.tree_combo_box.setItemText(3, QCoreApplication.translate("MainWindow", u"SwRS", None))

        self.edit_document_button.setText(QCoreApplication.translate("MainWindow", u"A", None))
        self.toolButton_2.setText(QCoreApplication.translate("MainWindow", u"D", None))
#if QT_CONFIG(tooltip)
        self.doc_review_tool_button.setToolTip(QCoreApplication.translate("MainWindow", u"Review all items in document.", None))
#endif // QT_CONFIG(tooltip)
        self.doc_review_tool_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.doc_clear_links_tool_button.setToolTip(QCoreApplication.translate("MainWindow", u"Clear all suspect links in document.", None))
#endif // QT_CONFIG(tooltip)
        self.doc_clear_links_tool_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.doc_reorder_level_tool_button.setToolTip(QCoreApplication.translate("MainWindow", u"Automatically reorder item levels in document.", None))
#endif // QT_CONFIG(tooltip)
        self.doc_reorder_level_tool_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.item_tree_search_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Filter...", None))
        self.item_tree_clear_search.setText(QCoreApplication.translate("MainWindow", u"C", None))
        ___qtreewidgetitem = self.item_tree_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Header", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Level", None));

        __sortingEnabled1 = self.item_tree_widget.isSortingEnabled()
        self.item_tree_widget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.item_tree_widget.topLevelItem(0)
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Header of chapter 1 [HEAD-1.0]", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"1.0", None));
        ___qtreewidgetitem2 = self.item_tree_widget.topLevelItem(1)
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("MainWindow", u"Header of chapter 2 [HEAD-2.0]", None));
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"2.0", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem2.child(0)
        ___qtreewidgetitem3.setText(1, QCoreApplication.translate("MainWindow", u"Requirement 1 [SwRS-12]", None));
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("MainWindow", u"2.1", None));
        self.item_tree_widget.setSortingEnabled(__sortingEnabled1)

        self.pinned_items_dock_widget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Pinned Items", None))
    # retranslateUi

