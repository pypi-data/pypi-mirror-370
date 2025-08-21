import os
import sys
import ctypes
import platform
import argparse
import logging
from qtpy import QtWidgets, QtGui, QtCore

from libreflow_launcher.model import Servers, Projects, Settings
from libreflow_launcher.controller import Controller
from libreflow_launcher.view import MainWindow


class SessionApp(QtWidgets.QApplication):

    def __init__(self, argv):
        super(SessionApp, self).__init__(argv)
        self.setApplicationName("Libreflow Launcher")

        self.parse_command_line_args(argv)

        QtGui.QFontDatabase.addApplicationFont(os.path.dirname(__file__)+'/ui/fonts/Asap-VariableFont_wdth,wght.ttf')
        self.setFont(QtGui.QFont('Asap', 9))

        QtCore.QDir.addSearchPath('icons.gui', os.path.dirname(__file__)+'/ui/icons/gui')

        css_file = os.path.dirname(__file__)+'/ui/styles/default/default_style.css'
        with open(css_file, 'r') as r:
            self.setStyleSheet(r.read())
        
        self.stream_formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
        self.logger = logging.getLogger('libreflow_launcher')
        self.logger.setLevel(logging.INFO)

        self.default_log_handler = logging.StreamHandler(sys.stdout)
        self.default_log_handler.setFormatter(self.stream_formatter)
        self.logger.addHandler(self.default_log_handler)

        # Connect everything together
        self.servers_model = Servers(self)
        self.projects_model = Projects(self)
        self.settings_model = Settings(self)

        self.ctrl = Controller(
            self, self.servers_model, self.projects_model, self.settings_model
        )

        self.offline = False

        #Auto start
        if self.autostart :
            success = self.auto_launch(self.autostart)
            if success:
                return
            else :
                self.log_error(f'Autostart {autostart} libreflow failed')

        #Check for connection to the api
        servers = self.ctrl.fetch_servers()
        self.ctrl.set_current_host()
        try:
            test_command = self.ctrl.api_get('/versions', json={})
            print(f'{test_command=}')
            if test_command is None:
                self.offline = True
                print(f'{self.offline=}')

        except: self.offline = True

        self.view = MainWindow(self.ctrl)
        
        self.view.show()
    
    def parse_command_line_args(self, args):
        parser = argparse.ArgumentParser(
            description='Libreflow Launcher Arguments'
        )

        parser.add_argument(
            '-S', '--site', dest='site', help='Site Name to use'
        )
        parser.add_argument(
            '--autostart', dest='autostart', help='Skip the launcher if user is assigned to a single project'
        )

        values, _ = parser.parse_known_args(args)

        if values.site:
            os.environ['LF_LAUNCHER_SITE_NAME'] = values.site
        
        self.autostart = values.autostart


    def log(self, context, *words):
        self._log(logging.INFO, ' '.join([str(i) for i in words]), extra={'context': context})

    def log_info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def log_debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def log_error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def log_warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def log_critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)

    def _log(self, level, message, *args, **kwargs):
        self.logger.log(level, message, *args, **kwargs)
    
    def auto_launch(self,project_name):

        servers = self.ctrl.fetch_servers()

        server_uid,project_uid,data = self.ctrl.get_server_from_project(project_name)

        self.ctrl.set_current_host(server_uid)

        if not self.ctrl.check_log_in():
            return False

        if not self.ctrl.check_site():
            return False

        # Get Remote
        project = self.ctrl.fetch_project(project_name)

        status = project['updated']

        if not status:
            updated_data = self.ctrl.update_project(project_uid)
            self.log_info(f"Updating {project_name} libreflow")

            data_resolve, env_folder = self.ctrl.update_project_env(project_name, project_uid)
            if data_resolve is None and env_folder is None:
                return

            updated_data = self.ctrl.update_project(project_uid,updated=True)

            update_exec_status = self.ctrl.update_project_exec(project_uid, data_resolve)
            if update_exec_status is False:
                return False

        # Start the instance
        self.log_info(f"Start {project_name} libreflow")
        start_status = self.ctrl.start_project(project_uid, data)

        if not start_status :
            return False

        return True


if __name__ == '__main__':
    if platform.system() == "Windows":
        myappid = 'lfscoop.libreflow_launcher'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = SessionApp(sys.argv)
    sys.exit(app.exec_())