import os
import re
import webbrowser
import platform
import subprocess

from qtpy import QtWidgets, QtGui, QtCore

from libreflow_launcher.ui import icons
import libreflow_launcher.resources as resources
from . import _version


class LabelIcon(QtWidgets.QLabel):

    def __init__(self, icon=None, size=None, color=None):
        QtWidgets.QLabel.__init__(self, '')
        if icon:
            self.setIcon(icon, size, color)
    
    def setIcon(self, icon, size=None, color=None):
        icon = QtGui.QIcon(resources.get_icon(icon, color=color))
        if size:
            size_value = QtCore.QSize(size, size)
        else:
            size_value = QtCore.QSize(16, 16)
        pixmap = icon.pixmap(size_value)
        self.setPixmap(pixmap)
        self.setAlignment(QtCore.Qt.AlignVCenter)


class LineEdit(QtWidgets.QLineEdit):

    def __init__(self, value=None, options=[], config_key=None, parent_widget=None):
        QtWidgets.QLineEdit.__init__(self)
        if value:
            self.setText(value)
        
        self.base_value = self.text()
        self.config_key = config_key
        self.options = options
        self.parent_widget = parent_widget

        if "path" in self.options:
            self.reveal_explorer()
        
        if "host" not in self.options:
            self.textChanged.connect(self._on_text_changed)

        self.editingFinished.connect(self._on_text_finish_edit)
        self.returnPressed.connect(self._on_enter_pressed)

    def reset(self):
        self.base_value = self.text()
        self.setProperty('edited', False)
        self.style().polish(self)

    def value_check(self):
        if self.text() == '':
            if "mandatory" in self.options:
                self.setProperty('warning', True)
                self.setToolTip('You cannot leave this parameter empty.')
                self.style().polish(self)
                return False
        
        if "host" in self.options:
            host_regex = r'^(?:\b(?!\bhttp[s]{0,1})([a-zA-Z\.\/]+)|(\d+\.\d+.\d+.\d+))(?::(\d{1,5}))?'
            if re.match(host_regex, self.text()) is None:
                self.setProperty('warning', True)
                self.setToolTip('Host format is not valid.')
                self.style().polish(self)
                return False

        return True

    def reveal_explorer(self):
        self.open_path = QtWidgets.QToolButton(self)
        self.open_path.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'open'))))
        self.open_path.setIconSize(QtCore.QSize(15,15))
        self.open_path.setStyleSheet('border: 0px; padding: 0px;')
        self.open_path.setCursor(QtCore.Qt.ArrowCursor)
        self.open_path.clicked.connect(self._on_explorer_button_clicked)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.open_path, 0, QtCore.Qt.AlignRight)

        layout.setSpacing(0)
        layout.setContentsMargins(5,5,5,5)

    def _on_text_changed(self):
        checked = self.value_check()
        if checked:
            if self.text() != self.base_value:
                self.setProperty('warning', False)
                self.setProperty('edited', True)
            else:
                self.setProperty('warning', False)
                self.setProperty('edited', False)
            self.setToolTip('')
        
        self.style().polish(self)
        if self.config_key:
            self.parent_widget._page.toggle_footer()

    def _on_text_finish_edit(self):
        self._on_text_changed()

    def _on_enter_pressed(self):
        self._on_text_finish_edit()
        self.parent().focusNextChild()
        focused_widget = QtWidgets.QApplication.focusWidget()
        if focused_widget.property('default'):
            focused_widget.clicked.emit()

    def _on_explorer_button_clicked(self):
        path = self.parent()._ctrl.resolve_value(self.text())
        if '{}' in path:
            path = path.split('{}')[0]
            self.parent()._mw.notification_header.pop("Open the most accessible folder", 'info', True)

        if os.path.isfile(path):
            path = os.path.dirname(path)

        if os.path.isdir(path):
            if platform.system() == 'Windows':
                return os.startfile(path)
            elif platform.system() == 'Linux':
                return subprocess.Popen(f'xdg-open "{path}"')
            else:
                return subprocess.Popen(f'open "{path}"')
        
        return self.parent()._mw.notification_header.pop("Path is not valid", 'error', True)


class ComboBox(QtWidgets.QComboBox):

    def __init__(self, items=None, config_key=None, parent=None):
        QtWidgets.QComboBox.__init__(self)
        if items:
            self.addItems(items)
        
        self.config_key = config_key
        self.parent = parent

    def enable_check(self):
        self.base_value = self.currentIndex()
        self.currentIndexChanged.connect(self._on_index_changed)
    
    def reset(self):
        self.base_value = self.currentIndex()
        self.setProperty('edited', False)
        self.style().polish(self)

    def _on_index_changed(self, i):
        if i != self.base_value:
            self.setProperty('edited', True)
        else:
            self.setProperty('edited', False)
        
        self.style().polish(self)
        if isinstance(self.parent, SettingsList):
            self.parent._page.toggle_footer()


class CheckBox(QtWidgets.QCheckBox):

    def __init__(self, state, comment=None, config_key=None, parent=None):
        QtWidgets.QCheckBox.__init__(self, comment)
        self.setChecked(state)

        self.config_key = config_key
        self.parent = parent

    def enable_check(self):
        self.base_value = self.isChecked()
        self.stateChanged.connect(self._on_state_changed)
    
    def reset(self):
        self.base_value = self.isChecked()
        self.setProperty('edited', False)
        self.style().polish(self)

    def _on_state_changed(self, i):
        if self.isChecked() != self.base_value:
            self.setProperty('edited', True)
        else:
            self.setProperty('edited', False)
        
        self.style().polish(self)
        self.parent._page.toggle_footer()


class MainWindow(QtWidgets.QWidget):

    def __init__(self, ctrl):
        QtWidgets.QWidget.__init__(self)
        self._ctrl = ctrl
        self._session = ctrl._session
        self.overlay_enabled = False

        self.setWindowIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'feespeciales_icon'))))
        self.resize(800, 600)
        
        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(0,0,0,0)

        background = QtWidgets.QFrame()
        background.setObjectName('Background')
        background.setStyleSheet(
            '''
            #Background {
                background-color: white;
            }
            '''
        )
        vlo.addWidget(background)

        self.grid_lo = QtWidgets.QGridLayout(background)
        self.grid_lo.setContentsMargins(0,0,0,0)

        self.menu_bar = MenuBar(self)
        self.wizard = WizardPage(self)
        self.warning = WarningPage(self)
        self.login = LoginPage(self)
        self.projects = ProjectsList(self)
        self.settings_bar = SettingsBar(self)
        self.settings_bar.hide()
        self.settings_page = SettingsPage(self)
        self.settings_bar.list._page = self.settings_page
        self.settings_page.hide()

        self.grid_lo.addWidget(self.menu_bar, 0, 0)
        self.grid_lo.addWidget(self.settings_bar, 0, 0)
        self.grid_lo.addWidget(self.wizard, 0, 1)
        self.grid_lo.addWidget(self.warning, 0, 1, QtCore.Qt.AlignCenter)
        self.grid_lo.addWidget(self.login, 0, 1, QtCore.Qt.AlignCenter)
        self.grid_lo.addWidget(self.projects, 0, 1)
        self.grid_lo.addWidget(self.settings_page, 0, 1)
        self.page_refresh('projects', force_update=True, init=True)
    
    def show_wizard(self, force_update=False, check=False):
        if check:
            self.menu_bar.servers.refresh(force_update)
            print(f'{self.menu_bar.servers.count()=}')
            if self.menu_bar.servers.count():
                return False

            self._session.log_info('Starting Wizard')

        for i in reversed(range(self.grid_lo.count())):
            widget = self.grid_lo.itemAt(i).widget()
            if (
                widget.objectName() == 'NotificationHeader' or 
                widget.objectName() == 'PopUpDialog' or 
                widget.objectName() == 'ServerHover'
            ):
                widget.deleteLater()
        
        self.overlay_enabled = False
        self.menu_bar.hide()
        if not check:
            self.wizard.redirect = True
        self.wizard.build()
        self.wizard.show()
        self.warning.hide()
        self.login.hide()
        self.projects.hide()
        self.settings_bar.hide()
        self.settings_page.hide()
        return True

    def page_refresh(self, redirect, force_update=False, init=False, logged=False):
        if self.show_wizard(force_update, True):
            return

        if not self.overlay_enabled:
            self.notification_header = NotificationHeader(self)
            self.popup = PopUpDialog(self)
            self.server_hover = ServerHover(self)
            self.grid_lo.addWidget(self.server_hover, 0, 0, 0, 2, QtCore.Qt.AlignTop)
            self.grid_lo.addWidget(self.notification_header, 0, 0, 0, 2, QtCore.Qt.AlignTop)
            self.grid_lo.addWidget(self.popup, 0, 0, 0, 2)
            self.overlay_enabled = True

        if redirect == 'projects':

            if force_update:
                self.projects.projects = []

            self.menu_bar.show()
            self.wizard.hide()
            self.settings_bar.hide()
            self.settings_page.hide()

            if init:
                self._ctrl.set_current_host()
                self._ctrl.update_python_current_version()
                self.menu_bar.servers.refresh()

            if logged or self._ctrl.check_log_in():
                self.login.hide()

                if init:
                    self.notification_header.pop('Connected', 'valid', True)

                check_site, assign_sites = self._ctrl.check_site()
                if check_site != 'valid':
                    self.projects.hide()
                    self.warning.build(check_site, assign_sites)
                    self.warning.show()
                    return
                
                self.warning.hide()
                self.projects.refresh()
                if self.projects.count() == 0:
                    self.projects.hide()
                    self.warning.build('projects_empty')
                    self.warning.show()
                    return
                else:
                    self.projects.show()
            else:
                if self._session.offline:
                    self.login.hide()
                    self.setWindowTitle("Libreflow Launcher(Offline)")
                    self.menu_bar.offline_icon.show()

                    if init:
                        self.notification_header.pop('Offline Mode', 'info', True)
                    
                    self.warning.hide()
                    self.projects.refresh()
                    if self.projects.count() == 0:
                        self.projects.hide()
                        self.warning.build('projects_empty')
                        self.warning.show()
                        return
                    else:
                        self.projects.show()

                else:
                    self.login.build()
                    self.login.show()
                    self.warning.hide()
                    self.projects.hide()
                    if self.menu_bar.servers.current_item:
                        self.menu_bar.servers.current_item.refresh()
            
            return
        
        if redirect == 'settings':
            self.settings_bar.list.refresh(True)
            if self.settings_bar.list.current_item.text() != 'Global':
                self.settings_bar.list.setSelected(self.settings_bar.list.layout.itemAt(0).widget())

            self.menu_bar.hide()
            self.login.hide()
            self.warning.hide()
            self.projects.hide()
            self.settings_bar.show()
            self.settings_page.refresh()
            self.settings_page.show()
            return

    def mousePressEvent(self, event):
        focused_widget = QtWidgets.QApplication.focusWidget()
        if isinstance(focused_widget, LineEdit) or isinstance(focused_widget, ComboBox):
            focused_widget.clearFocus()
        QtWidgets.QMainWindow.mousePressEvent(self, event)


class PopUpDialog(QtWidgets.QFrame):

    ICONS = {
        "delete": ('icons.gui', 'trash_normal')
    }
    DESCRIPTION = {
        "delete": "You're sure you want to delete this {item_type}"
    }

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self.setObjectName('PopUpDialog')

        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session
        self._signal_primary = None
        self._signal_secondary = None

        self.hide()
        self.build()

    def build(self):
        self.container_lo = QtWidgets.QVBoxLayout(self)
        
        self.message_widget = QtWidgets.QFrame()
        self.message_widget.setObjectName('PopUpMessage')
        self.message_widget.setFixedWidth(300)
        self.message_lo = QtWidgets.QVBoxLayout(self.message_widget)
        self.message_lo.setSpacing(10)

        self.icon_lo = QtWidgets.QVBoxLayout()
        self.icon_lo.setContentsMargins(20,20,20,20)
        self.message_lo.addLayout(self.icon_lo)

        self.icon_lbl = LabelIcon()
        self.icon_lo.addWidget(self.icon_lbl)

        self.main_label = QtWidgets.QLabel()
        self.main_label.setWordWrap(True)
        self.main_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_label.setObjectName('PopUpMainLabel')
        self.description_label = QtWidgets.QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setAlignment(QtCore.Qt.AlignCenter)

        self.message_lo.addWidget(self.main_label)
        self.message_lo.addWidget(self.description_label)

        self.input_lo = QtWidgets.QVBoxLayout()
        self.message_lo.addLayout(self.input_lo)
        self.input_text = LineEdit()
        self.input_text.setObjectName("SettingsInput")
        self.input_lo.addWidget(self.input_text)
        self.input_text.hide()

        self.buttons_lo = QtWidgets.QHBoxLayout()
        self.buttons_lo.setContentsMargins(10,10,10,20)
        self.message_lo.addLayout(self.buttons_lo)

        self.secondary_btn = QtWidgets.QPushButton('Cancel')
        self.secondary_btn.setObjectName('PopUpButton')
        self.secondary_btn.clicked.connect(self._on_secondary_button_clicked)
        self.buttons_lo.addWidget(self.secondary_btn)

        self.primary_btn = QtWidgets.QPushButton('')
        self.primary_btn.setObjectName('PopUpButton')
        self.primary_btn.clicked.connect(self._on_primary_button_clicked)
        self.buttons_lo.addWidget(self.primary_btn)

        self.container_lo.addWidget(self.message_widget, alignment=QtCore.Qt.AlignCenter)

    def pop(self, action, p_type=None, value=None, signal_primary=None, signal_secondary=None):
        self._mw.popup.show()
        self._type = p_type
        self._signal_primary = signal_primary
        self._signal_secondary = signal_secondary
        
        if action == 'delete':
            self.icon_lbl.setIcon(self.ICONS.get(action), 50)
            self.icon_lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.main_label.setText(f'{action.capitalize()} {value}?')
            self.description_label.setText(self.DESCRIPTION.get(action).format(item_type=self._type))
            self.input_text.hide()
            self.primary_btn.setText(action.capitalize())
            self.primary_btn.setProperty(action, True)
            self.primary_btn.style().polish(self.primary_btn)
            self.primary_btn.show()
            self.secondary_btn.show()
            return
        
        if action == 'updating' or action == 'launching' or action == 'uninstall':
            self.icon_lbl.hide()
            self.main_label.setText(f'{action.capitalize()} Libreflow')
            self.description_label.setText('Please wait...')
            self.input_text.hide()
            self.secondary_btn.hide()
            self.primary_btn.hide()
            return
        
        if action == 'python_path':
            self.icon_lbl.hide()
            self.main_label.setText('Enter your python path')
            self.input_text.show()
            self.primary_btn.setText('Set')
            self.primary_btn.setProperty(action, True)
            self.primary_btn.style().polish(self.primary_btn)
            self.primary_btn.show()
            self.secondary_btn.show()
            return

    def _on_secondary_button_clicked(self):
        if self._signal_secondary is not None:
            code = self._signal_secondary()
            if code:
                return
        
        self.input_text.clear()
        self.hide()

    def _on_primary_button_clicked(self):
        if self._signal_primary is not None:
            code = self._signal_primary()
            if code:
                return

        self.input_text.clear()
        self.hide()


class NotificationHeader(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self.setObjectName('NotificationHeader')

        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session

        self.hide()

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
      
        container_lo = QtWidgets.QVBoxLayout(self)
        
        self.message_widget = QtWidgets.QFrame()
        message_lo = QtWidgets.QHBoxLayout(self.message_widget)

        self.message_widget.setObjectName('NotificationMessage')
        self.message_widget.setFixedWidth(400)

        self.label = QtWidgets.QLabel('')
        self.label.setWordWrap(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        message_lo.addWidget(self.label)

        container_lo.addWidget(self.message_widget, 0, QtCore.Qt.AlignCenter)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._hide_message)

    def pop(self, text, n_type, temporary=False):
        self._mw.notification_header.show()
        self._type = n_type
        self.label.setText(text)
        self.message_widget.setProperty(self._type, True)
        self.message_widget.style().polish(self.message_widget)
        if temporary:
            self.timer.start(4000)
    
    def _hide_message(self):
        self.message_widget.setProperty(self._type, False)
        self._mw.notification_header.hide()
        self.timer.stop()


class ServerHover(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self.setObjectName('ServerHover')
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self._mw = mw
        self._ctrl = mw._ctrl
        self._servers_list = mw.menu_bar.servers
        self._session = mw._session

        self.ref_geometry = None
        self.width = None
        self.height = None

        self.hide()
        self.build()

    def build(self):
        self.container_lo = QtWidgets.QVBoxLayout(self)
        
        self.box_widget = QtWidgets.QWidget()
        self.box_widget.setObjectName('BoxWidget')
        self.box_widget.setFixedHeight(57)
        self.box_widget.installEventFilter(self)
        box_lo = QtWidgets.QHBoxLayout(self.box_widget)
        box_lo.setContentsMargins(0,0,0,0)

        horizontal_spacer = QtWidgets.QSpacerItem(
            self._mw.menu_bar.width(), 0, 
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        box_lo.addItem(horizontal_spacer)

        self.box_frame = QtWidgets.QFrame()
        box_frame_lo = QtWidgets.QVBoxLayout(self.box_frame)
        box_lo.addWidget(self.box_frame)

        self.box_frame.setStyleSheet('background-color: #f2eff1; border-radius: 5px;')
        self.box_frame.setFixedWidth(200)
        self.box_frame.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        server_lo = QtWidgets.QHBoxLayout()
        box_frame_lo.addLayout(server_lo)

        self.server_icon = LabelIcon(('icons.gui', 'server'))
        self.server_label = QtWidgets.QLabel('')
        self.server_label.setWordWrap(True)
        # server_lo.addWidget(self.server_icon)
        server_lo.addWidget(self.server_label)
        server_lo.addStretch()

        user_lo = QtWidgets.QHBoxLayout()
        box_frame_lo.addLayout(user_lo)

        self.user_label = QtWidgets.QLabel('')
        self.user_label.setWordWrap(True)

        self.refresh_btn = QtWidgets.QToolButton()
        self.refresh_btn.setObjectName('ServerRefreshButton')
        self.refresh_btn.clicked.connect(self._on_refresh_button_clicked)

        self.user_log_out = QtWidgets.QToolButton()
        self.user_log_out.setObjectName('ServerLogOutButton')
        self.user_log_out.clicked.connect(self._on_log_out_button_clicked)

        user_lo.addWidget(self.user_label)
        user_lo.addStretch()
        user_lo.addWidget(self.refresh_btn)
        user_lo.setSpacing(1)
        user_lo.addWidget(self.user_log_out)

        self.container_lo.addWidget(self.box_widget)

    def settingMask(self):
        self.region = QtGui.QRegion(self.frameGeometry())
        coord = QtCore.QPoint(
            self._mw.menu_bar.layout().getContentsMargins()[0]+self.width,
            self._mw.menu_bar.layout().getContentsMargins()[1]+self.height
        )
        self.ref_geometry.moveTopLeft(coord)
        self.region -= QtGui.QRegion(self.ref_geometry, QtGui.QRegion.Ellipse)
        self.setMask(self.region)

    def pop(self, server):
        self.ref_geometry = server.circle.frameGeometry()
        self.width = server.circle.frameGeometry().x()
        self.height = server.frameGeometry().y()

        self.container_lo.setContentsMargins(9,9 + self.height,9,9)
        self.server_label.setText(server._data['display_name'])
        if (
            not isinstance(server, ServerAddButton) # Is a actual server
            and server._current_user and self._servers_list.current_item == server # Is currently used
        ):
            text_label = server._current_user
            text_label += f' ({self._ctrl.current_site})' if self._mw.warning.isVisible() is False else ''
            self.user_label.setText(text_label)
            self.user_label.show()
            self.refresh_btn.show()
            self.user_log_out.show()
        else:
            self.user_label.hide()
            self.refresh_btn.hide()
            self.user_log_out.hide()
        
        self.settingMask()
        self.show()

    def resizeEvent(self, event):
        if self.ref_geometry:
            self.settingMask()

    def eventFilter(self, obj, event):
        if obj.objectName() == 'BoxWidget':
            if event.type() == QtCore.QEvent.Enter:
                return True
            elif event.type() == QtCore.QEvent.Leave:
                self.hide()
                return True
        return False

    def _on_log_out_button_clicked(self):
        self._ctrl.log_out()
        self._mw.page_refresh('projects', True)
        self.hide()

    def _on_refresh_button_clicked(self):
        self._mw.page_refresh('projects', True)
        self.hide()
        self._mw.notification_header.pop("Server updated", 'valid', True)


class WizardPage(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session

        self.redirect = False

        self.container_lo = QtWidgets.QGridLayout(self)
        
    def build(self):
        if self.container_lo.count() > 0:
            for i in reversed(range(self.container_lo.count())):
                self.container_lo.itemAt(i).widget().deleteLater()
        
        if not self.redirect:
            self.landing = self.landing_screen()
            self.container_lo.addWidget(self.landing, 0, 0, QtCore.Qt.AlignCenter)
        
        self.close = self.close_button()
        self.container_lo.addWidget(self.close, 0, 0, 0, 1, QtCore.Qt.AlignTop)
        self.close.hide()

        self.setup = self.server_setup()
        self.container_lo.addWidget(self.setup, 0, 0, QtCore.Qt.AlignCenter)
        self.reset_inputs()

        self.redirect = False

    def landing_screen(self):
        landing_widget = QtWidgets.QWidget()
        landing_lo = QtWidgets.QVBoxLayout(landing_widget)

        main_text = QtWidgets.QLabel('Welcome to Libreflow Launcher!')
        main_text.setStyleSheet('font-weight: bold; font-size: 36px;')
        landing_lo.addWidget(main_text, 0, QtCore.Qt.AlignCenter)

        start_button = QtWidgets.QPushButton('Let\'s add a server')
        start_button.setAutoDefault(True)
        start_button.setObjectName('LoginButton')
        start_button.clicked.connect(self._on_start_button_clicked)
        landing_lo.addWidget(start_button, 0, QtCore.Qt.AlignCenter)

        return landing_widget

    def server_setup(self):
        server_widget = QtWidgets.QWidget()
        if not self.redirect:
            server_widget.hide()
        else:
            self.close.show()
        
        self.server_lo = QtWidgets.QVBoxLayout(server_widget)

        main_text = QtWidgets.QLabel('Enter server parameters')
        main_text.setStyleSheet('font-weight: bold; font-size: 36px;')
        self.server_lo.addWidget(main_text, 0, QtCore.Qt.AlignCenter)

        self.name_input = LineEdit(options=['mandatory'])
        self.name_input.setObjectName('ServerInput')
        self.name_input.setPlaceholderText('Server name')
        self.server_lo.addWidget(self.name_input, 0, QtCore.Qt.AlignCenter)
        
        self.host_input = LineEdit(options=['mandatory', 'host'])
        self.host_input.setObjectName('ServerInput')
        self.host_input.setPlaceholderText('Host')
        self.server_lo.addWidget(self.host_input, 0, QtCore.Qt.AlignCenter)

        add_button = QtWidgets.QPushButton('Add')
        add_button.setObjectName('LoginButton')
        add_button.setDefault(True)
        add_button.clicked.connect(self._on_add_button_clicked)
        self.server_lo.addWidget(add_button, 0, QtCore.Qt.AlignCenter)

        return server_widget

    def close_button(self):
        close_widget = QtWidgets.QWidget()
        close_lo = QtWidgets.QHBoxLayout(close_widget)
        close_lo.addStretch()
        
        close_btn = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'close'), color=QtGui.QColor('#26262f')), ''
        )
        close_btn.setObjectName('MenuBarButton')
        close_btn.clicked.connect(self._on_close_button_clicked)
        close_lo.addWidget(close_btn)

        return close_widget

    def reset_inputs(self):
        self.name_input.reset()
        self.host_input.reset()

    def _on_start_button_clicked(self):
        self.landing.hide()
        self.setup.show()

    def _on_add_button_clicked(self):
        for i in range(self.server_lo.count()):
            widget = self.server_lo.itemAt(i).widget()
            if widget.property('warning'):
                return

        api_host = self.host_input.text()
        
        # Set default port, 5500 for local or 80 for public address
        if re.search(r"^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$", api_host):
            api_port = '5500'
        else:
            api_port = '80'
        
        if ':' in self.host_input.text():
            api_host, api_port = self.host_input.text().split(':')

        data = dict(
            display_name=self.name_input.text(),
            api_host=api_host,
            api_port=api_port
        )
        uid = self._ctrl.update_server(data)

        if uid :
            self._session.offline = False

        if self.redirect:
            self._mw.menu_bar.servers.refresh(True)
            self.redirect = False

        self._mw.page_refresh('projects', True)

    def _on_close_button_clicked(self):
        self._mw.page_refresh('projects', True)


class WarningPage(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session
       
        self.warning_lo = QtWidgets.QVBoxLayout(self)

    def build(self, error_code, site_names=None):
        if self.warning_lo.count() > 0:
            for i in reversed(range(self.warning_lo.count())):
                self.warning_lo.itemAt(i).widget().deleteLater()

        self.icon = LabelIcon(('icons.gui', 'alert'), 100, color=QtGui.QColor('#f2eff1'))
        self.warning_lo.addWidget(self.icon, 0, QtCore.Qt.AlignCenter)

        self.title = QtWidgets.QLabel('')
        self.title.setStyleSheet('font-weight: bold; font-size: 24px;')
        self.warning_lo.addWidget(self.title, 0, QtCore.Qt.AlignCenter)

        self.subtitle = QtWidgets.QLabel('')
        self.warning_lo.addWidget(self.subtitle, 0, QtCore.Qt.AlignCenter)
        self.subtitle.hide()

        self.site_input = ComboBox()
        self.site_input.setObjectName('LoginCombobox')
        self.site_input.view().window().setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        self.site_input.view().window().setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.warning_lo.addWidget(self.site_input, 0, QtCore.Qt.AlignCenter)
        self.site_input.hide()

        self.select_button = QtWidgets.QPushButton('Select')
        self.select_button.setObjectName('LoginButton')
        self.select_button.setDefault(True)
        self.select_button.clicked.connect(self._on_select_button_clicked)
        self.warning_lo.addWidget(self.select_button, 0, QtCore.Qt.AlignCenter)
        self.select_button.hide()

        self.refresh(error_code, site_names)

    def refresh(self, error_code, site_names=None):
        # Projects list empty
        if error_code == 'projects_empty':
            self.title.setText('You are not assigned to any project.')
        # Site errors
        if error_code == 'no_sites':
            self.title.setText('No sites are defined on the server.')
        if error_code == 'argument':
            self.title.setText('Choose the site you would like to use')
            self.icon.hide()
        elif error_code == 'unknown':
            self.title.setText(f'Site {self._ctrl.current_site} do not exist.')
        elif error_code == 'disabled':
            self.title.setText(f'Site {self._ctrl.current_site} is disabled.')
        elif error_code == 'archived':
            self.title.setText(f'Site {self._ctrl.current_site} is archived.')
        elif error_code == 'assigned':
            self.title.setText(f'You are not assigned to {self._ctrl.current_site} site.')
        elif error_code == 'not_assigned':
            self.title.setText(f'You are not assigned to any site.')

        # If user are assigned to other sites, show combobox selection.
        if error_code not in ['no_sites', 'not_assigned', 'projects_empty'] and site_names:
            if error_code != 'argument':
                self.subtitle.setText('You can select an another site.')
                self.subtitle.show()
            self.site_input.addItems(site_names)
            self.site_input.show()
            self.site_input.enable_check()
            self.select_button.show()

    def _on_select_button_clicked(self):
        self._ctrl.update_settings({'current_site': self.site_input.currentText()})
        self._mw.page_refresh('projects', True, logged=True)


class SettingsPage(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self._mw = mw
        self._sb = mw.settings_bar
        self._ctrl = mw._ctrl
        self._session = mw._session

        self.page_lo = QtWidgets.QVBoxLayout(self)

        self.settings_changed = False

        self.build()

    def build(self):
        header = QtWidgets.QHBoxLayout()
        self.page_lo.addLayout(header)
        
        self.page_text = QtWidgets.QLabel('')
        self.page_text.setStyleSheet('font-weight: bold; font-size: 24px;')
        header.addWidget(self.page_text)

        self.delete_btn = QtWidgets.QToolButton()
        self.delete_btn.setObjectName("SettingsDeleteButton")
        self.delete_btn.clicked.connect(self._on_delete_button_clicked)
        header.addWidget(self.delete_btn)
        
        header.addStretch()
        
        close_btn = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'close'), color=QtGui.QColor('#26262f')), ''
        )
        close_btn.setObjectName('MenuBarButton')
        close_btn.clicked.connect(self._on_close_button_clicked)
        header.addWidget(close_btn)

        self.content = QtWidgets.QGridLayout()
        # Left, top, right, bottom
        self.content.setContentsMargins(0, 20, 0, 20)
        self.page_lo.addLayout(self.content)

        self.stretch_widget = QtWidgets.QWidget()
        stretch_lo = QtWidgets.QVBoxLayout(self.stretch_widget)
        self.page_lo.addWidget(self.stretch_widget)

        self.footer_empty = QtWidgets.QWidget()
        self.footer_empty.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.footer_empty_lo = QtWidgets.QHBoxLayout(self.footer_empty)
        self.footer_empty_lo.setContentsMargins(0,0,0,0)
        self.page_lo.addWidget(self.footer_empty)
        
        spacer = QtWidgets.QSpacerItem(0, 27, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.footer_empty_lo.addItem(spacer)
        
        self.footer = QtWidgets.QWidget()
        self.footer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        footer_lo = QtWidgets.QHBoxLayout(self.footer)
        footer_lo.setContentsMargins(0,0,0,0)
        self.page_lo.addWidget(self.footer)
        self.footer.hide()

        cancel_btn = QtWidgets.QPushButton('Cancel')
        cancel_btn.setObjectName('SettingsFooterButton')
        cancel_btn.clicked.connect(self._on_cancel_button_clicked)
        self.save_btn = QtWidgets.QPushButton('Save')
        self.save_btn.setObjectName("SettingsFooterButton")
        self.save_btn.clicked.connect(self._on_save_button_clicked)

        footer_lo.addStretch()
        footer_lo.addWidget(cancel_btn)
        footer_lo.addWidget(self.save_btn)
    
    def refresh(self):

        self.settings_changed = False

        self.current_item = self._sb.list.current_item
        if self.current_item.elided:
            self.page_text.setText(self.current_item.full_text)
        else:
            self.page_text.setText(self.current_item.text())

        if self.content.count() > 0:
            for i in reversed(range(self.content.count())):
                self.content.itemAt(i).widget().deleteLater()

        for i, group in enumerate(self.current_item.get_content()):
            for x, widget in enumerate(group):
                self.content.addWidget(widget, i, x)
        
        if type(self.current_item._data) == dict:
            self.delete_btn.show()
        else:
            self.delete_btn.hide()
        
        if self.current_item._data == "About":
            self.page_text.setText('')
            self.stretch_widget.hide()
        else:
            self.stretch_widget.show()

        self.footer_empty.show()
        self.footer.hide()

    def toggle_footer(self):
        for i in range(self.content.count()):
            widget = self.content.itemAt(i).widget()
            if widget.property('edited'):
                self.footer_empty.hide()
                self.footer.show()
                return
        
        self.footer_empty.show()
        self.footer.hide()

    def update_python_custom_paths(self, tree):
        data = []
        for i in range(tree.topLevelItemCount()):
            item = tree.topLevelItem(i)
            if item:
                if '&custom' in item.path:
                    data.append({
                        'version': item.version,
                        'path': item.path
                    })
        
        return self._ctrl.update_python_custom_paths(data)

    def _on_close_button_clicked(self):
        self._mw.page_refresh('projects', self.settings_changed)

    def _on_delete_button_clicked(self):
        if self._mw.popup.isVisible():
            self._ctrl.remove_server(self.current_item._data['uid'])
            self._mw.menu_bar.servers.refresh(True)
            self._mw.menu_bar.servers.orderChanged.emit(self._mw.menu_bar.servers.get_order_data())
            self._sb.list.refresh(True)
            self._mw.settings_page.refresh()
            self.settings_changed = True
            return self._mw.notification_header.pop('Server deleted', 'valid', True)

        self._mw.popup.pop('delete', 'server', self.page_text.text(), self._on_delete_button_clicked)

    def _on_cancel_button_clicked(self):
        self.refresh()

    def _on_save_button_clicked(self):
        data = {}
        for i in range(self.content.count()):
            widget = self.content.itemAt(i).widget()
            if widget.property('warning'):
                return self._mw.notification_header.pop("One or more inputs are incorrect", 'error', True)

            if widget.property('edited'):
                if isinstance(widget, LineEdit):
                    if widget.config_key == 'api_host':
                        data[widget.config_key] = widget.text().split(':')[0]
                        data['api_port'] = widget.text().split(':')[1]
                    else:
                        data[widget.config_key] = widget.text()
                if isinstance(widget, QtWidgets.QTreeWidget):
                    if widget.config_key == 'python_path':
                        data['python_path'] = widget.currentItem().path.replace('&custom', '')
                        data['is_custom_path'] = widget.currentItem().is_custom
                        data['python_version'] = widget.currentItem().version
                        self.update_python_custom_paths(widget)
                    else:
                        data[widget.config_key] = widget.currentData()
                if isinstance(widget, CheckBox):
                    data[widget.config_key] = widget.isChecked()
                
                widget.reset()
        
        focused_widget = QtWidgets.QApplication.focusWidget()
        focused_widget.clearFocus()
        
        if type(self.current_item._data) == dict:
            self._ctrl.update_server(data, self.current_item._data['uid'])
            self._ctrl.set_current_host()
            self.current_item.refresh()
            self.refresh()
        else:
            self._ctrl.update_settings(data)
        
        self.settings_changed = True
        
        self._mw.notification_header.pop("Saved", 'valid', True)
        self.toggle_footer()


class SettingsContent(QtWidgets.QPushButton):

    def __init__(self, settings_list, data):
        super(SettingsContent, self).__init__('')
        self.setObjectName('SettingsButton')
        self.setProperty('selected', False)

        self.settings_list = settings_list
        self._data = data
        self._mw = settings_list._mw
        self._ctrl = settings_list._ctrl
        self._session = settings_list._session

        self.elided = False
        self.full_text = None
        
        self.refresh()

    def refresh(self):
        if type(self._data) == str:
            self.setText(self._data)
        else:
            self.setText(self._data['display_name'])

        if len(self.text()) > 20:
            self.elided = True
            self.full_text = self.text()
            self.setText(''.join([x[0].upper() for x in self.text().split(' ')]))
    
    def setSelected(self):
        if not self.property('selected'):
            self.setProperty('selected', True)
            self.style().polish(self)
        else:
            self.setProperty('selected', False)
            self.style().polish(self)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.settings_list.current_item == self:
                return
            
            self.settings_list.setSelected(self)


class DeletePythonPath(QtWidgets.QWidget):

    def __init__(self, tree, item):
        super(DeletePythonPath, self).__init__(tree)
        self.tree = tree

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.button = QtWidgets.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(resources.get_icon(('icons.gui', 'close'))))
        self.button.setIconSize(QtCore.QSize(10,10))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(lambda checked=False, x=item: self._on_delete_button_clicked(x))

        layout.addStretch()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def _on_delete_button_clicked(self, item):
        self.tree.delete_mode = True
        self.tree.takeTopLevelItem(self.tree.indexFromItem(item).row())
        self.tree.delete_mode = False

        self.tree.list_check()


class PythonPathItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, tree, version, path):
        super(PythonPathItem, self).__init__(tree)
        self.tree = tree
        self.parent_widget = tree.parent_widget
        
        self.version = version
        self.path = path
        self.is_custom = bool('&custom' in path)

        self.refresh()
    
    def refresh(self):
        self.setText(0, self.version)
        self.setText(1, self.path.replace('&custom', ''))


class PythonPathsList(QtWidgets.QTreeWidget):

    def __init__(self, parent_widget, data, config_key):
        super(PythonPathsList, self).__init__()
        self.parent_widget = parent_widget
        self.data = data
        self.config_key = config_key
        self.base_value = None
        self.paths_count = 0
        self.delete_mode = False

        self.setHeaderLabels(self.get_columns())
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
        self.setRootIsDecorated(False)
        
        self.init_mode = True
        self.currentItemChanged.connect(self._on_item_select)
        self.refresh()
        self.init_mode = False

        # self.view().window().setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.FramelessWindowHint | QtCore.Qt.NoDropShadowWindowHint)
        # self.view().window().setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # self.header().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        # self.setColumnWidth(0, self.columnWidth(0)+30)

        # self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self._on_context_menu)

    def get_columns(self):
        return ('Version', 'Path')

    def sizeHint(self):
        return QtCore.QSize(0, 120)

    def refresh(self):
        # Fetch current path
        if self.data.get('is_custom_path', False) == True:
            python_selected_path = f"{self.data['python_path']}&custom"
        else:
            python_selected_path = self.data['python_path']

        # Fetch default versions
        python_versions = self.parent_widget._mw._ctrl.fetch_python_versions()
        for version_data in python_versions:
            item = PythonPathItem(self, version_data['version'], version_data['path'])
            if version_data['path'] == python_selected_path:
                self.setCurrentItem(item)

        # Fetch custom paths
        python_custom_paths = self.parent_widget._mw._ctrl.fetch_python_custom_paths()
        if python_custom_paths is not None:
            for version_data in python_custom_paths:
                item = PythonPathItem(self, version_data['version'], version_data['path'])
                # Add delete button
                self.setItemWidget(item, 1, DeletePythonPath(self, item))
                if version_data['path'] == python_selected_path:
                    self.setCurrentItem(item)
        
        PythonPathItem(self, '', 'Add Path')
        
        self.base_value = self.currentItem()
        self.paths_count = self.topLevelItemCount()-1

    def list_check(self):
        if not self.init_mode:
            if self.currentItem() != self.base_value or self.topLevelItemCount()-1 != self.paths_count:
                self.setProperty('edited', True)
            else:
                self.setProperty('edited', False)
        
        self.style().polish(self)

        if self.currentItem().path == 'Add Path':
            if self.delete_mode == True:
                return self.setCurrentItem(self.base_value)
            else:
                return self.parent_widget._mw.popup.pop(
                    'python_path',
                    signal_primary=self._on_set_button_clicked,
                    signal_secondary=self._on_cancel_button_clicked
                )

        self.parent_widget.settings_list._page.toggle_footer()

    def reset(self):
        self.base_value = self.currentItem()
        self.setProperty('edited', False)
        self.style().polish(self)

    def _on_item_select(self, current, previous):
        if current is None:
            base_font = previous.font(1)
            base_font.setWeight(QtGui.QFont.Normal)
            for i in range(self.header().count()): 
                if previous:
                    previous.setFont(i, base_font)
            
            self.setCurrentItem(self.topLevelItem(0))
            return

        bold_font = current.font(1)
        bold_font.setWeight(QtGui.QFont.Bold)
        
        base_font = current.font(1)
        base_font.setWeight(QtGui.QFont.Normal)

        for i in range(self.header().count()):
            current.setFont(i, bold_font)    
            if previous:
                previous.setFont(i, base_font)
        
        self.list_check()

    # Those signals are for the python path popup
    def _on_set_button_clicked(self):
        input_text = self.parent_widget._mw.popup.input_text
        # Fetch python number
        path = input_text.text()

        # Check if already added
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item:
                if path == item.path:
                    input_text.setProperty('warning', True)
                    input_text.setToolTip('Path already added to list.')
                    input_text.style().polish(input_text)
                    return True
        
        # Check if path is valid
        if self.parent_widget._ctrl.fetch_python_version(path) is None:
            input_text.setProperty('warning', True)
            input_text.setToolTip('Path is not valid.\nCan\'t exec --version command.')
            input_text.style().polish(input_text)
            return True
        
        self.takeTopLevelItem(self.indexFromItem(self.currentItem()).row())

        item = PythonPathItem(self, self.parent_widget._ctrl.fetch_python_version(path), f'{path}&custom')
        
        # Add delete button
        self.setItemWidget(item, 1, DeletePythonPath(self, item))

        self.setCurrentItem(item)

        PythonPathItem(self, '', 'Add Path')
    
    def _on_cancel_button_clicked(self):
        self.setCurrentItem(self.base_value)


class GlobalSettings(SettingsContent):

    def get_content(self):
        contents = []

        data = self._ctrl.fetch_settings()

        install_label = QtWidgets.QLabel("Installation directory")
        install_input = LineEdit(
            data['install_dir'],
            ['mandatory', 'path'],
            'install_dir',
            self.settings_list
        )
        install_input.setObjectName("SettingsInput")
        first_group = [install_label, install_input]
        contents.append(first_group)

        python_label = QtWidgets.QLabel("Default python version")
        python_input = PythonPathsList(self, data, 'python_path')
        python_input.setObjectName("SettingsInputList")

        second_group = [python_label, python_input]
        contents.append(second_group)

        site_label = QtWidgets.QLabel("Current site")
        site_input = LineEdit(
            data['current_site'],
            config_key='current_site',
            parent_widget=self.settings_list
        )
        site_input.setObjectName("SettingsInput")
        third_group = [site_label, site_input]
        contents.append(third_group)

        show_process_label = QtWidgets.QLabel("Show Process View")
        show_process_input = CheckBox(
            data.get('show_process_view', False),
            '(works if not in project config)',
            config_key="show_process_view",
            parent=self.settings_list
        )
        show_process_input.setObjectName("SettingsCheckBox")
        quarter_group = [show_process_label, show_process_input]
        contents.append(quarter_group)

        show_process_input.enable_check()

        advanced_label = QtWidgets.QLabel("Advanced Mode")
        advanced_input = CheckBox(
            data.get('advanced_mode', False),
            config_key="advanced_mode",
            parent=self.settings_list
        )
        advanced_input.setObjectName("SettingsCheckBox")
        fifth_group = [advanced_label, advanced_input]
        contents.append(fifth_group)

        advanced_input.enable_check()

        return contents


class ServerSettings(SettingsContent):

    def get_content(self):
        contents = []

        name_label = QtWidgets.QLabel("Host name")
        name_input = LineEdit(
            self._data['display_name'],
            ['mandatory'],
            'display_name',
            self.settings_list
        )
        name_input.setObjectName("SettingsInput")
        first_group = [name_label, name_input]
        contents.append(first_group)

        host_label = QtWidgets.QLabel("Host address")
        host_input = LineEdit(
            f"{self._data['api_host']}:{self._data['api_port']}",
            ['mandatory', 'host'],
            'api_host',
            self.settings_list
        )
        host_input.setObjectName("SettingsInput")
        second_group = [host_label, host_input]
        contents.append(second_group)

        return contents


class About(SettingsContent):

    def get_content(self):
        contents = []

        about_widget = QtWidgets.QWidget()
        
        about_lo = QtWidgets.QVBoxLayout(about_widget)
        about_lo.setContentsMargins(0,0,0,0)

        about_lo.addStretch()

        logo = LabelIcon(('icons.gui', 'feespeciales_icon'), 100)
        about_lo.addWidget(logo, 0, QtCore.Qt.AlignCenter)

        software_text = QtWidgets.QLabel('Libreflow Launcher')
        software_text.setStyleSheet('font-weight: bold; font-size: 36px;')
        about_lo.addWidget(software_text, 0, QtCore.Qt.AlignCenter)

        version_text = QtWidgets.QLabel(f"Version {_version.get_versions()['version']}")
        about_lo.addWidget(version_text, 0, QtCore.Qt.AlignCenter)

        web_buttons = QtWidgets.QWidget()
        web_buttons_lo = QtWidgets.QHBoxLayout(web_buttons)
        
        gitlab_btn = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'gitlab')), 'GitLab'
        )
        gitlab_btn.setIconSize(QtCore.QSize(30,30))
        gitlab_btn.setObjectName("GitLabButton")
        gitlab_btn.clicked.connect(self._on_gitlab_button_clicked)
        web_buttons_lo.addWidget(gitlab_btn)

        pypi_btn = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'pypi')), 'PyPI'
        )
        pypi_btn.setIconSize(QtCore.QSize(30,30))
        pypi_btn.setObjectName("PyPIButton")
        pypi_btn.clicked.connect(self._on_pypi_button_clicked)
        web_buttons_lo.addWidget(pypi_btn)

        about_lo.addWidget(web_buttons, 0, QtCore.Qt.AlignCenter)
        about_lo.addStretch()

        contents.append([about_widget])

        return contents
    
    def _on_gitlab_button_clicked(self):
        webbrowser.open("https://gitlab.com/lfs.coop/libreflow/libreflow_launcher")

    def _on_pypi_button_clicked(self):
        webbrowser.open("https://pypi.org/project/libreflow-launcher/")


class SettingsList(QtWidgets.QScrollArea):

    def __init__(self, sb):
        super(SettingsList, self).__init__()
        self._sb = sb
        self._mw = sb._mw
        self._ctrl = sb._ctrl
        self._session = sb._session
        self._page = None

        self.current_item = None

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.setStyleSheet(
            '''
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            '''
        )

    def refresh(self, force_update=False):
        if force_update:
            self.current_item = None

            container = QtWidgets.QWidget()
            container.setObjectName('ScrollAreaContainer')
            container.setStyleSheet(
                '''
                #ScrollAreaContainer {
                    background-color: transparent;
                    border: none;
                }
                '''
            )
            self.layout = QtWidgets.QVBoxLayout(container)
            self.layout.setAlignment(QtCore.Qt.AlignTop)
            # self.layout.setSpacing(30)

            global_btn = GlobalSettings(self, 'Global')
            self.layout.addWidget(global_btn)
        
            for i in range(self._mw.menu_bar.servers.count()):
                widget = self._mw.menu_bar.servers.layout.itemAt(i).widget()
                if widget:
                    btn = ServerSettings(self, widget._data)
                    self.layout.addWidget(btn)
            
            about_btn = About(self, 'About')
            self.layout.addWidget(about_btn)

            self.layout.addStretch(1)

            # Left, top, right, bottom
            self.layout.setContentsMargins(0,0,0,0)
            self.setWidget(container)

        self.setSelected()

    def count(self):
        return self.layout.count()-1

    def setSelected(self, item=None):
        if not self.current_item:
            for i in range(self.layout.count()):
                item = self.layout.itemAt(i).widget()
                if item:
                    if item.text() == "Global":
                        item.setSelected()
                        self.current_item = item
                        break
            return

        self.current_item.setSelected()
        self.current_item = item
        self.current_item.setSelected()
        self._mw.settings_page.refresh()


class SettingsBar(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session

        self.setFixedWidth(175)
        self.setObjectName('MenuBar')
        self.setStyleSheet('#MenuBar { background-color: #f2eff1; }')
       
        vlo = QtWidgets.QVBoxLayout(self)
        # vlo.setContentsMargins(0,0,0,0)

        self.list = SettingsList(self)
        vlo.addWidget(self.list)
        vlo.addStretch()


class ServerAddButton(QtWidgets.QWidget):

    def __init__(self, servers_list):
        super(ServerAddButton, self).__init__()
        self.setFixedHeight(45)

        self.servers_list = servers_list
        self._mw = servers_list._mw
        self._ctrl = servers_list._ctrl
        self._session = servers_list._session

        # For server hover
        self._data = {
            'display_name': 'Add a server'
        }

        self.build()

    def build(self):
        container = QtWidgets.QGridLayout(self)
        container.setContentsMargins(0,0,0,0)

        self.circle = QtWidgets.QWidget()
        self.circle.setFixedSize(45,45)
        self.circle.setObjectName('ServerAddButton')
        self.circle.installEventFilter(self)
        circle_lo = QtWidgets.QVBoxLayout(self.circle)
        circle_lo.setContentsMargins(0,0,0,0)

        self.icon = LabelIcon(('icons.gui', 'plus'), color=QtGui.QColor('#26262f'))
        self.icon.setAlignment(QtCore.Qt.AlignVCenter)
        circle_lo.addWidget(self.icon, alignment=QtCore.Qt.AlignCenter)

        container.addWidget(self.circle, 0, 0, alignment=QtCore.Qt.AlignCenter)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            if not self._mw.server_hover.isVisible():
                self._mw.server_hover.pop(self)
            return True
        return False

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mw.show_wizard()


class ServerItem(QtWidgets.QWidget):

    def __init__(self, servers_list, data, current_user):
        super(ServerItem, self).__init__()
        self.setFixedHeight(45)

        self.servers_list = servers_list
        self._data = data
        self._current_user = current_user
        self._mw = servers_list._mw
        self._ctrl = servers_list._ctrl
        self._session = servers_list._session

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            
        # shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        # shadow.setBlurRadius(40)
        # shadow.setXOffset(0)
        # shadow.setYOffset(5)
        # shadow.setColor(QtGui.QColor(0, 0, 0, 81))
        # self.setGraphicsEffect(shadow)
        
        self.build()

    def build(self):
        container = QtWidgets.QGridLayout(self)
        container.setContentsMargins(0,0,0,0)

        self.circle = QtWidgets.QWidget()
        self.circle.setFixedSize(45,45)
        self.circle.setObjectName('ServerItem')
        self.circle.setProperty('selected', False)
        self.circle.installEventFilter(self)
        circle_lo = QtWidgets.QVBoxLayout(self.circle)
        circle_lo.setContentsMargins(0,0,0,0)

        self.text = QtWidgets.QLabel(self._data['code'])
        self.text.setObjectName('ServerItem')
        self.text.setProperty('selected', False)
        self.text.setAlignment(QtCore.Qt.AlignVCenter)
        circle_lo.addWidget(self.text, alignment=QtCore.Qt.AlignCenter)

        container.addWidget(self.circle, 0, 0, alignment=QtCore.Qt.AlignCenter)

        self.arrow = LabelIcon(('icons.gui', 'arrow-right'), 7, QtGui.QColor('white'))
        self.arrow.setAlignment(QtCore.Qt.AlignCenter)
        self.arrow.setFixedSize(15,15)
        self.arrow.setStyleSheet('border-radius: 7px; background-color: #5553ac;')
        self.arrow.installEventFilter(self)
        container.addWidget(self.arrow, 0, 0, alignment=QtCore.Qt.AlignRight)
        self.arrow.hide()

    def refresh(self):
        self._current_user = self._ctrl.fetch_user_name(self._data['uid'])

    def setSelected(self):
        if not self.circle.property('selected'):
            self.circle.setProperty('selected', True)
            self.text.setProperty('selected', True)
            self.arrow.show()
        else:
            self.circle.setProperty('selected', False)
            self.text.setProperty('selected', False)
            self.arrow.hide()
        self.circle.style().polish(self.circle)
        self.text.style().polish(self.text)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Enter:
            if not self._mw.server_hover.isVisible():
                self._mw.server_hover.pop(self)
            return True
        return False

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self._mw.server_hover.hide()

            drag = QtGui.QDrag(self)
            mime = QtCore.QMimeData()
            drag.setMimeData(mime)
            drag.setHotSpot(QtCore.QPoint(25, 25))
            
            pixmap = QtGui.QPixmap(self.size())
            pixmap.fill(QtCore.Qt.transparent)
            self.render(pixmap)
            drag.setPixmap(pixmap)

            store_status = self.circle.property('selected')
            self.circle.setProperty('selected', False)
            self.circle.setProperty('drag', True)
            self.text.setProperty('selected', False)
            self.circle.style().polish(self.circle)
            self.text.style().polish(self.text)
            self.text.hide()
            self.arrow.hide()
            
            drag.exec_(QtCore.Qt.MoveAction)

            self.text.show()
            self.circle.setProperty('drag', False)
            self.circle.style().polish(self.circle)
            if store_status:
                self.setSelected()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.servers_list._ctrl.server_uid == self._data['uid']:
                return
            
            self.servers_list._ctrl.set_current_host(self._data['uid'])
            self._mw.page_refresh('projects')


class ServersList(QtWidgets.QScrollArea):

    orderChanged = QtCore.Signal(list)

    def __init__(self, mb):
        super(ServersList, self).__init__()
        self._mb = mb
        self._mw = mb._mw
        self._ctrl = mb._ctrl
        self._session = mb._session

        self.current_item = None

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setAcceptDrops(True)

        self.setStyleSheet(
            '''
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar {
                height: 0px;
            }
            '''
        )

    def refresh(self, force_update=False):
        if force_update:
            self.current_item = None
            servers = self._ctrl.fetch_servers()

            container = QtWidgets.QWidget()
            container.setObjectName('ScrollAreaContainer')
            container.setStyleSheet(
                '''
                #ScrollAreaContainer {
                    background-color: transparent;
                    border: none;
                }
                '''
            )
            self.layout = QtWidgets.QVBoxLayout(container)
            self.layout.setAlignment(QtCore.Qt.AlignTop)
        
            for server in servers:
                current_user = self._ctrl.fetch_user_name(server['uid'])
                item = ServerItem(self, server, current_user)
                self.layout.addWidget(item)
            

            add_server = ServerAddButton(self)
            self.layout.addWidget(add_server)

            if self._session.offline:
                add_server.setVisible(False)
            
            # Left, top, right, bottom
            self.layout.setContentsMargins(0,0,0,0)
            self.setWidget(container)

            # Auto set if there is only one server
            if len(servers) == 1 and self._ctrl.server_uid == None:
                self._ctrl.set_current_host(server['uid'])

        self.setSelected()

    def count(self):
        return self.layout.count()-1

    def setSelected(self):
        # Unselect
        if self.current_item:
            index = self.layout.indexOf(self.current_item)
            self.layout.itemAt(index).widget().setSelected()

        # Select
        current_host = self._ctrl.server_uid
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i).widget()
            if isinstance(item, ServerItem):
                if item._data['uid'] == current_host:
                    item.setSelected()
                    self.current_item = item
                    break

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        pos = event.pos()
        source_widget = event.source()

        # Check if we don't drop on the same widget
        if not source_widget.geometry().contains(pos):
            target_widget = None
            for i in range(self.layout.count()):
                w = self.layout.itemAt(i).widget()
                if w.geometry().contains(pos):
                    target_widget = w
            if target_widget is None or isinstance(target_widget, ServerAddButton):
                return
            
            self.layout.insertWidget(self.layout.indexOf(target_widget), source_widget)
            self.orderChanged.emit(self.get_order_data())

        event.accept()

    def get_order_data(self):
        data = []
        for i in range(self.count()):
            item = self.layout.itemAt(i).widget()
            data.append(item._data['uid'])
        
        self._ctrl.update_servers_order(data)
        return data


class MenuBar(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session

        self.setFixedWidth(75)
        self.setObjectName('MenuBar')
        self.setStyleSheet('#MenuBar { background-color: #f2eff1; }')
       
        vlo = QtWidgets.QVBoxLayout(self)
        vlo.setContentsMargins(9,15,9,15)

        self.servers = ServersList(self)
        vlo.addWidget(self.servers)


        self.offline_icon = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'wifi_off')), ''
        )
        self.offline_icon.setObjectName('MenuBarButton')
        self.offline_icon.setToolTip('The Overseer server is unavailable, Launcher is set to Offline mode')
        vlo.addWidget(self.offline_icon, alignment=QtCore.Qt.AlignCenter)
        self.offline_icon.hide()


        settings_btn = QtWidgets.QPushButton(
            resources.get_icon(('icons.gui', 'settings_outline'), color=QtGui.QColor('#26262f')), ''
        )
        settings_btn.setObjectName('MenuBarButton')
        settings_btn.clicked.connect(self._on_settings_button_clicked)
        vlo.addWidget(settings_btn, alignment=QtCore.Qt.AlignCenter)
       
    def _on_settings_button_clicked(self):
        self._mw.page_refresh('settings')



class LoginPage(QtWidgets.QFrame):

    def __init__(self, mw):
        QtWidgets.QFrame.__init__(self)
        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session
       
        self.login_lo = QtWidgets.QVBoxLayout(self)

    def build(self):
        if self.login_lo.count() > 0:
            for i in reversed(range(self.login_lo.count())):
                self.login_lo.itemAt(i).widget().deleteLater()

        logo = LabelIcon(('icons.gui', 'feespeciales_icon'), 100)
        self.login_lo.addWidget(logo, 0, QtCore.Qt.AlignCenter)

        self.login_input = LineEdit()
        self.login_input.setObjectName('LoginInput')
        self.login_input.setPlaceholderText('Login')
        self.login_lo.addWidget(self.login_input, 0, QtCore.Qt.AlignCenter)

        self.password_input = LineEdit()
        self.password_input.setObjectName('LoginInput')
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login_lo.addWidget(self.password_input, 0, QtCore.Qt.AlignCenter)

        connect_button = QtWidgets.QPushButton('Connect')
        connect_button.setObjectName('LoginButton')
        connect_button.setDefault(True)
        connect_button.clicked.connect(self._on_connect_button_clicked)
        self.login_lo.addWidget(connect_button, 0, QtCore.Qt.AlignCenter)

    def _on_connect_button_clicked(self):
        # Keep only username if login is a mail address
        log_in = self.login_input.text()
        if re.match('^[\w\-\.]+@(?:[\w-]+\.)+[\w-]{2,4}$', log_in):
            log_in, _ = self.login_input.text().split('@')

        logged_in = self._ctrl.log_in(log_in, self.password_input.text())
        if logged_in:
            self._mw.page_refresh('projects', True, logged=True)
            self._mw.notification_header.pop('Connected', 'valid', True)
        else:
            self._mw.notification_header.pop('Authentification invalid', 'error', True)


class ProjectItem(QtWidgets.QWidget):

    def __init__(self, projects_list, data):
        super(ProjectItem, self).__init__()
        self.setObjectName('ProjectItem')

        self.projects_list = projects_list
        self._mw = projects_list._mw
        self._ctrl = projects_list._ctrl
        self._session = projects_list._session

        self._status = data['updated']
        self._data = data['data']
        self._uid = self._data['uid']
            
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        ### For grid view
        # self.setMaximumWidth(335)
        # self.setMaximumHeight(200)

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QtGui.QColor(0, 0, 0, 81))
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(
            '''
            QLabel {
                color: white;
            }
            #ProjectItem {
                background-color: #2f2e5f;
                border-radius: 10px;
            }
            '''
        )

        self.build()
        self.refresh()

    def build(self):
        container = QtWidgets.QVBoxLayout(self)
        container.setContentsMargins(20,10,20,10)

        footer = QtWidgets.QWidget()
        footer_lo = QtWidgets.QHBoxLayout(footer)
        footer_lo.setContentsMargins(0,0,0,0)
        container.addWidget(footer, alignment=QtCore.Qt.AlignBottom)

        self.status_lbl = QtWidgets.QLabel('')
        footer_lo.addWidget(self.status_lbl, alignment=QtCore.Qt.AlignVCenter)

        self.project_name = QtWidgets.QLabel()
        self.project_name.setStyleSheet('color: white; font-size: 24px;')

        footer_lo.addWidget(self.project_name, alignment=QtCore.Qt.AlignVCenter)
        footer_lo.addStretch()

        kitsu_button = QtWidgets.QPushButton(QtGui.QIcon(resources.get_icon(('icons.gui', 'kitsu'))), '')
        kitsu_button.setObjectName('ProjectButton')
        kitsu_button.clicked.connect(self._on_kitsu_button_clicked)

        self.start_button = QtWidgets.QPushButton(
            QtGui.QIcon(resources.get_icon(('icons.gui', 'start'), color=QtGui.QColor('white'))), ''
        )
        self.start_button.setObjectName('ProjectButton')

        if not self._session.offline:
            self.start_button.clicked.connect(lambda: self._on_start_button_clicked())

        else: self.start_button.clicked.connect(lambda: self._on_skip_updates_clicked())

        self.start_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.start_button.customContextMenuRequested.connect(self._on_context_menu)

        footer_lo.addWidget(kitsu_button, alignment=QtCore.Qt.AlignVCenter)
        footer_lo.addWidget(self.start_button, alignment=QtCore.Qt.AlignVCenter)

    def refresh(self, data=None):
        if data:
            self._status = data['updated']
            self._data = data['data']

        if self._session.offline :
            color = QtGui.QColor('#DDD')
            self.status_lbl.setToolTip("Offline - Update status unavailable")

        elif self._status is True:
            color = QtGui.QColor('#4eb16f')
            self.status_lbl.setToolTip("Ready to launch")
        elif self._status is False:
            color = QtGui.QColor('#d5972a')
            self.status_lbl.setToolTip("Needs to be updated")
        else:
            color = QtGui.QColor('#d5972a')
            self.status_lbl.setToolTip("Waiting for first install")

        self.circular_shape = QtGui.QIcon(
            resources.get_icon(('icons.gui', 'circular-shape-silhouette'), color=color)
        )
        pixmap = self.circular_shape.pixmap(QtCore.QSize(24, 24))
        self.status_lbl.setPixmap(pixmap)

        self.project_name.setText(self._data['name'])

    def _on_kitsu_button_clicked(self):
        webbrowser.open(self._data['kitsu_url'])

    def _on_start_button_clicked(self, exec_mode=None):
        # Update instance if config has changed
        if not self._status:
            updated_data = self._ctrl.update_project(self._uid)

            self._session.log_info(f"Updating {self._data['name']} libreflow")
            self._mw.popup.pop('updating')
            QtWidgets.QApplication.processEvents()
            
            data_resolve, env_folder = self._ctrl.update_project_env(self._data['name'], self._uid)
            if data_resolve is None and env_folder is None:
                self._mw.notification_header.pop("Error has occurred. Check console.", 'error', True)
                self._mw.popup.hide()
                return
            
            updated_data = self._ctrl.update_project(self._uid, updated=True)
            
            self.refresh(updated_data)
            
            update_exec_status = self._ctrl.update_project_exec(self._uid, data_resolve)
            if update_exec_status is False:
                self._mw.notification_header.pop("Error has occurred. Check console.", 'error', True)
                self._mw.popup.hide()
                return

        # Start the instance
        self._session.log_info(f"Start {self._data['name']} libreflow {exec_mode if exec_mode else ''}")
        start_status = self._ctrl.start_project(self._uid, self._data, exec_mode)
        
        # Update project status if error
        if start_status is False:
            self._mw.notification_header.pop("Error has occurred. Check console.", 'error', True)
            updated_data = self._ctrl.update_project(self._uid, updated=None)
            self.refresh(updated_data)

        self._mw.popup.hide()

    def _on_start_terminal_clicked(self, exec_mode):
        self._ctrl.start_terminal(self._uid, exec_mode)

    def _on_force_update_clicked(self):
        self._session.log_info(f"Updating {self._data['name']} libreflow")
        self._mw.popup.pop('updating')
        QtWidgets.QApplication.processEvents()
        
        data_resolve, env_folder = self._ctrl.update_project_env(self._data['name'], self._uid)
        if data_resolve is None and env_folder is None:
            self._mw.notification_header.pop("Error has occurred. Check console.", 'error', True)
            self._mw.popup.hide()
            return

        updated_data = self._ctrl.update_project(self._uid, updated=True)    
        
        self.refresh(updated_data)
        
        update_exec_status = self._ctrl.update_project_exec(self._uid, data_resolve)
        if update_exec_status is False:
            self._mw.notification_header.pop("Error has occurred. Check console.", 'error', True)
            self._mw.popup.hide()
            return

        self._session.log_info(f"Start {self._data['name']} libreflow")
        self._ctrl.start_project(self._uid, self._data)

        self._mw.popup.hide()

    def _on_skip_updates_clicked(self, exec_mode=None):

        # Start the instance
        self._session.log_info(f"Start {self._data['name']} libreflow {exec_mode if exec_mode else ''}")
        start_status = self._ctrl.start_project(self._uid, self._data, exec_mode)
        
        # Update project status if error
        if start_status is False:
            self._mw.notification_header.pop("Error has occurred. Check console.", 'error', True)
            updated_data = self._ctrl.update_project(self._uid, updated=None)
            self.refresh(updated_data)

        self._mw.popup.hide()

    def _on_uninstall_clicked(self):
        self._session.log_info(f"Uninstall {self._data['name']} libreflow")
        self._mw.popup.pop('uninstall')
        QtWidgets.QApplication.processEvents()

        self._ctrl.uninstall_project(self._uid)

        updated_data = self._ctrl.update_project(self._uid)
        self.refresh(updated_data)

        self._mw.popup.hide()

        self._mw.notification_header.pop("Project has been uninstalled.", "valid", True)

    def _on_reinstall_clicked(self):
        self._on_uninstall_clicked()
        self._on_start_button_clicked()

    def _on_context_menu(self, event):
        context_menu = QtWidgets.QMenu(self)

        update_action = QtWidgets.QAction('Force update', self)
        update_action.triggered.connect(self._on_force_update_clicked)

        context_menu.addAction(update_action)

        skip_update_action = QtWidgets.QAction('Skip updates', self)
        skip_update_action.triggered.connect(lambda: self._on_skip_updates_clicked())

        context_menu.addAction(skip_update_action)

        if self._ctrl.fetch_advanced_mode():
            uninstall_action = QtWidgets.QAction('Uninstall', self)
            uninstall_action.triggered.connect(self._on_uninstall_clicked)

            reinstall_action = QtWidgets.QAction('Reinstall', self)
            reinstall_action.triggered.connect(self._on_reinstall_clicked)

            start_sync_action = QtWidgets.QAction('Start sync session', self)
            start_sync_action.triggered.connect(lambda: self._on_start_button_clicked('sync'))

            start_jobs_action = QtWidgets.QAction('Start jobs session', self)
            start_jobs_action.triggered.connect(lambda: self._on_start_button_clicked('jobs'))

            start_index_action = QtWidgets.QAction('Start index session', self)
            start_index_action.triggered.connect(lambda: self._on_start_button_clicked('index'))

            start_request_action = None
            if self._ctrl.check_exec(self._uid, 'request'):
                start_request_action = QtWidgets.QAction('Start request session', self)
                start_request_action.triggered.connect(lambda: self._on_start_button_clicked('request'))

            start_terminal_action = QtWidgets.QAction('Start terminal', self)
            start_terminal_action.triggered.connect(lambda: self._on_start_terminal_clicked('terminal'))

            clear_cache_action = QtWidgets.QAction('Clear pypi cache', self)
            clear_cache_action.triggered.connect(lambda: self._on_start_terminal_clicked('cache'))

            context_menu.addAction(uninstall_action)
            context_menu.addAction(reinstall_action)

            context_menu.addSeparator()

            context_menu.addAction(start_sync_action)
            context_menu.addAction(start_jobs_action)
            context_menu.addAction(start_index_action)
            if start_request_action:
                context_menu.addAction(start_request_action)
            context_menu.addAction(start_terminal_action)
            context_menu.addAction(clear_cache_action)

        context_menu.exec_(self.start_button.mapToGlobal(event))


class ProjectsList(QtWidgets.QTableWidget):

    def __init__(self, mw):
        super(ProjectsList, self).__init__()
        self._mw = mw
        self._ctrl = mw._ctrl
        self._session = mw._session

        self.cellsContent = []
        self.projects = []

        ### For grid view
        # self.cellWidth = 335
        # self.cellHeight = 200
        self.cellPadding = 15
        
        ### For grid view
        # self.currentColumnCount = self.viewport().width() // self.cellWidth
        # self.setColumnCount(self.currentColumnCount)
        self.setColumnCount(1)

        self.setShowGrid(False)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.setStyleSheet(
            f'''
            QTableWidget {{
                background-color: transparent;
                border: none;
            }}
            '''
        )
    
    def refresh(self):
        self.blockSignals(True)

        if self.count() > 0:
            for cell in self.cellsContent:
                self.removeCellWidget(cell[0], cell[1])
            
            self.cellsContent = []

        if self.projects == [] :
            if not self._session.offline:
                self.projects = self._ctrl.fetch_projects()
            else : self.projects = self._ctrl.fetch_cached_projects()
        _projects = sorted(self.projects, key=lambda p: p['data']['name'])

        for project in _projects:
            start_r, start_c = self.get_last_idx()
            if start_c == 0:
                self.setRowCount(start_r + 1)

            if project['server_uid'] == self._ctrl.server_uid:
                item = ProjectItem(self, project)
                lo = QtWidgets.QHBoxLayout()
                lo.addWidget(item)
                lo.setContentsMargins(self.cellPadding, self.cellPadding, self.cellPadding, self.cellPadding)

                widget = QtWidgets.QWidget()
                widget.setLayout(lo)
                self.setCellWidget(start_r, start_c, widget)
                self.setRowHeight(start_r, 81)

                self.cellsContent.append((start_r, start_c, widget))
        
        self.blockSignals(False)

    def get_last_idx(self):
        last_r, last_c = divmod(self.count(), self.columnCount())
        return last_r, last_c

    def count(self):
        return len(self.cellsContent)

    def resizeEvent(self, event):
        ### For grid view
        ### TODO: Find why it crashes after a project was added or deleted
        # possibleColumn = self.viewport().width() // 335
        # if possibleColumn == 0:
        #     possibleColumn = 1
        
        # # Reorder widgets
        # if possibleColumn != self.currentColumnCount:
        #     # Remove all widgets
        #     for cell in self.cellsContent:
        #         self.removeCellWidget(cell[0], cell[1])

        #     # Set new column count
        #     self.setColumnCount(possibleColumn)
        #     self.currentColumnCount = possibleColumn

        #     # Re-add widgets
        #     for c, cell in enumerate(self.cellsContent):
        #         row_index, column_index, widget = cell[0], cell[1], cell[2]

        #         start_r, start_c = divmod(c, self.columnCount())
        #         if start_c == 0:
        #             self.setRowCount(start_r + 1)

        #         self.setCellWidget(start_r, start_c, widget)
        #         self.cellsContent[c] = (start_r, start_c, widget)
        
        # Set column width and row height
        ### Fixed row height for grid view
        ### Fixed row height based on widget height itself
        # column_width = self.viewport().width() // self.currentColumnCount
        column_width = self.viewport().width() // 1
        # for r_idx in range(self.rowCount()):
        #     self.setRowHeight(r_idx, self.cellHeight)
        for c_idx in range(self.columnCount()):
            self.setColumnWidth(c_idx, column_width)

        return super().resizeEvent(event)
