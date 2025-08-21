import sys
import shutil
import os
import json
import pprint
import pathlib
import re
import unicodedata
import uuid
import platform


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')

def user_settings_folder():
    return os.path.join(pathlib.Path.home(), '.libreflow_launcher')


class Servers():

    def __init__(self, session):
        self._session = session
        self._servers = []
        self.servers_dir = os.path.dirname(__file__)+'/data/servers'

    def fetch_servers(self):
        self._servers = []

        for server in os.listdir(self.servers_dir):
            uid, ext = os.path.splitext(server)
            if ext == '.json':
                config_path = os.path.join(self.servers_dir, server)
                with open(config_path, "r") as f:
                    data = json.loads(f.read())

                self._servers.append(data)
        
        # Sort by name if no user preference
        self._servers = sorted(self._servers, key=lambda s: s['display_name'])
        
        try:
            f = open(f"{user_settings_folder()}/user_servers_order.json", "r")
        except IOError:
            pass
        else:
            user_data = json.load(f)['uid_list']

            # Check if a server has been added
            servers_uids = [s['uid'] for s in self._servers]
            new_uid = [uid for uid in servers_uids if uid not in user_data]

            # Update user servers order file
            if new_uid:
                user_data.append(new_uid[0])
                with open(f"{user_settings_folder()}/user_servers_order.json", 'w+') as f:
                    json.dump(dict(uid_list=user_data), f, indent=4)

            self._servers = sorted(self._servers, key=lambda s: user_data.index(s['uid']))
            f.close()

        self._session.log_info(f'Fetch {len(self._servers)} servers')
        return self._servers

    def fetch_server(self, uid):
        item = [s for s in self._servers if s['uid'] == uid]
        return item[0]

    def update_server(self, data, uid=None):
        config_path = os.path.join(self.servers_dir, '{uid}.json')

        if not uid:
            uid = str(uuid.uuid4())
            data.update(dict(
                code=''.join([x[0].upper() for x in data['display_name'].split(' ')]),
                uid=uid,
            ))
        else:
            for i, s in enumerate(self._servers):
                if s['uid'] == uid:
                    for key in data:
                        if key == 'display_name':
                            self._servers[i]['code'] = ''.join([x[0].upper() for x in data[key].split(' ')])
                        self._servers[i][key] = data[key]
                    data = self._servers[i]

        config_path = config_path.format(uid=uid)
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=4)
        
        return uid

    def remove_server(self, uid):
        for server in os.listdir(self.servers_dir):
            local_uid, ext = os.path.splitext(server)
            if local_uid == uid and ext == '.json':
                config_path = os.path.join(self.servers_dir, server)
                os.remove(config_path)

                for i, s in enumerate(self._servers):
                    if s['uid'] == uid:
                        self._servers.pop(i)
                        break


class Projects():

    def __init__(self, session):
        self._session = session
        self._projects = []
        self.projects_dir = f'{user_settings_folder()}/projects'
    
    def get_server_from_project(self, name):
        for project_uid in os.listdir(self.projects_dir):

            project_path = f'{self.projects_dir}/{project_uid}'
            config_path = os.path.join(project_path, 'config.json')

            path = f"{project_path}/__{name}__.txt"
            if os.path.exists(path):
                with open(path, "r") as f:
                    ph = json.loads(f.read())
                
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        data = json.loads(f.read())
                    
                        return ph['host_uid'],project_uid, data

    def fetch_projects(self, data_remote, server_uid):
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
        
        # Clear all projects loaded
        self._projects = [loaded_data for loaded_data in self._projects if loaded_data['server_uid'] != server_uid]

        if not self._session.offline:
            for remote in data_remote:
                status = True
                data = remote

                local_path = f'{self.projects_dir}/{remote["uid"]}'
                config_path = os.path.join(local_path, 'config.json')

                # Check if remote has changed
                if os.path.exists(config_path):
                    with open(config_path, "r") as f:
                        local = json.loads(f.read())
                        data = local

                    if local != remote:
                        status = False
                    
                else:
                    os.makedirs(local_path)
                    with open(config_path, 'w') as f:
                        json.dump(remote, f, indent=4)
                
                # Make a placeholder file
                with open(f"{local_path}/__{data['name']}__.txt", 'w') as f:
                    d = dict(host_uid = self._session.ctrl.server_uid)
                    json.dump(d, f)
                
                # Check if there is a venv
                env_folder = os.path.join(local_path, 'env')
                if not os.path.exists(env_folder):
                    status = None
                else:
                    env_status = self._session.ctrl.check_env(remote["uid"], remote["name"])
                    if env_status is None:
                        status = None
                    elif env_status is False:
                        status = False

                self._projects.append(dict(server_uid=server_uid, updated=status, data=data))

            self._session.log_info(f'Fetch {len(data_remote)} projects')
        
        else:
            for project_uid in os.listdir(self.projects_dir):
                status = True
                project_path = f'{self.projects_dir}/{project_uid}'
                config_path = os.path.join(project_path, 'config.json')

                if os.path.exists(config_path):
                    with open(config_path,"r") as f:
                        data = json.loads(f.read())
                
                    ph_path = f"{project_path}/__{data['name']}__.txt"
                    with open(ph_path, 'r') as f:
                        try:
                            ph = json.loads(f.read())
                        except:
                            continue
                    
                    if ph['host_uid'] == server_uid:
                    
                        # Check if there is a venv
                        env_folder = os.path.join(project_path, 'env')
                        if os.path.exists(env_folder):
                            env_status = self._session.ctrl.check_env(data["uid"], data["name"])
                            if env_status is None:
                                status = None
                                continue
                            elif env_status is False:
                                status = False

                            self._projects.append(dict(server_uid=server_uid, updated=status, data=data))

            
            self._session.log_info(f'Fetch {len(self._projects)} projects')
        
        return self._projects

    def update_project(self, data_remote, updated=None):
        local_path = f'{self.projects_dir}/{data_remote["uid"]}'
        config_path = os.path.join(local_path, 'config.json')

        for i, loaded_data in enumerate(self._projects):
            if loaded_data['data']['uid'] == data_remote['uid']:
                with open(config_path, 'w') as f:
                    json.dump(data_remote, f, indent=4)

                self._projects[i]['data'] = data_remote
                self._projects[i]['updated'] = updated
                break
        
        return self._projects[i]


class Settings():

    def __init__(self, session):
        self._session = session
        self._settings = {}
        
        self.settings_path = os.path.join(user_settings_folder(), 'user_settings.json')
        self.python_custom_paths = os.path.join(user_settings_folder(), 'python_custom_paths.json')
        
        self.fetch_settings()

    def fetch_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                local = json.loads(f.read())
            
            if 'current_site' not in local.keys():
                local['current_site'] = os.getenv('LF_LAUNCHER_SITE_NAME', None)
                self.update_settings(local)
            else:
                site_env = os.getenv('LF_LAUNCHER_SITE_NAME', None)
                if site_env is not None and site_env != local['current_site']:
                    local['current_site'] = site_env
                    self.update_settings(local)
            
            self._settings.update(local)
        else:
            if not os.path.exists(user_settings_folder()):
                os.makedirs(user_settings_folder())
            
            with open(self.settings_path, 'w') as f:
                default_data = dict(
                    install_dir="{user_settings}/projects/{project_uid}/env",
                    python_path=sys.executable,
                    is_custom_path=False,
                    python_version=re.match(r"([^\s]+)", sys.version).group(1),
                    current_site=os.getenv('LF_LAUNCHER_SITE_NAME', None),
                    show_process_view=False,
                    advanced_mode=False
                )
                json.dump(default_data, f, indent=4)
                self._settings.update(default_data)
        
        return self._settings
    
    def fetch_key(self, key):
        return self._settings.get(key, None)
    
    def update_settings(self, data):
        for key in data:
            self._settings[key] = data[key]

        with open(self.settings_path, 'w') as f:
            json.dump(self._settings, f, indent=4)

    def fetch_python_custom_paths(self):
        if os.path.exists(self.python_custom_paths):
            with open(self.python_custom_paths, "r") as f:
                return json.loads(f.read())
        
        return None

    def update_python_custom_paths(self, data):
        with open(self.python_custom_paths, 'w') as f:
            json.dump(data, f, indent=4)
