from pprint import pprint
from collections import OrderedDict
from packaging.version import Version
from packaging.specifiers import SpecifierSet
import os
import shutil
import requests
import pathlib
import unicodedata
import json
import platform
import subprocess
import toml
import re


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


class Controller():

    BASE_URL = 'http://0.0.0.0:5500'
    
    server_name = None
    server_uid = None
    
    current_user = None
    current_site = None
    
    CONFIG = {'headers': None}
    
    python_path = None

    def __init__(self, session, servers, projects, settings):
        self._session = session
        self._servers = servers
        self._projects = projects
        self._settings = settings

    def api_get(self, route, json):
        try:
            resp = requests.get(
                self.BASE_URL + route, json=json,
                headers=self.CONFIG['headers']
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return resp.json()
        except requests.exceptions.RequestException as err:
            # self._session.offline = True
            self._session.log_error(err)
            return None
        else:
            return resp.json()

    def api_post(self, route, json):
        try:
            resp = requests.post(
                self.BASE_URL + route, json=json,
                headers=self.CONFIG['headers']
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return resp.json()
        except requests.exceptions.RequestException as err:
            self._session.log_error(err)
            return None
        else:
            return resp.json()

    def api_patch(self, route, json):
        try:
            resp = requests.patch(
                self.BASE_URL + route, json=json,
                headers=self.CONFIG['headers']
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return resp.json()
        except requests.exceptions.RequestException as err:
            self._session.log_error(err)
            return None
        else:
            return resp.json()

    def get_token(self, data: dict) -> str:
        try:
            resp = requests.post(
                self.BASE_URL + '/token', data=data, allow_redirects=False
            )
            # Handle HTTPS redirect
            if resp.status_code == 301 or resp.status_code == 308:
                https_url = resp.headers['Location']
                resp = requests.post(https_url, data=data)
                if resp.status_code == 200:
                    self.BASE_URL = https_url.replace('/token', '')

            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return resp.json()
        except requests.exceptions.RequestException as err:
            self._session.offline = True
            self._session.log_error(err)
            return None
        else:
            return resp.json()


    def set_current_host(self, uid=None):
        user_settings_folder = self.user_settings_folder()
        if not os.path.exists(user_settings_folder):
            os.makedirs(user_settings_folder)

        restore = False
        if uid is None:
            try:
                f = open(f"{user_settings_folder}/current_host.json", "r")
            except IOError:
                return
            else:
                data = json.load(f)
                uid = data['uid']
                restore = True
                f.close()

        server = self._servers.fetch_server(uid)

        self.BASE_URL = f'http://{server["api_host"]}:{server["api_port"]}'
        self.server_name = server["display_name"]
        self.server_uid = uid

        if user_settings_folder is not None and restore is False:
            with open(f"{user_settings_folder}/current_host.json", 'w+') as f:
                json.dump(dict(
                    uid=self.server_uid
                ), f, indent=4)
        
        self.current_site = self._settings.fetch_key('current_site')

    def log_in(self, login, password):
        try :
            token = self.get_token({'username': login, 'password': password})
        except :
            self._session.offline = True

        if token is None:
            self._session.log_error(f'Connection failed to {self.server_name} server, {self.BASE_URL}')
            return False
        elif 'detail' in token and token['detail'] == "invalid-auth":
            self._session.log_error(f'Authentification invalid to {self.server_name} server, {self.BASE_URL}')
            return False

        self.CONFIG['headers'] = {
            'Authorization': 'Bearer {}'.format(token['access_token'])
        }
        self.current_user = login

        user_settings_folder = self.user_settings_folder()
        if not os.path.exists(user_settings_folder):
            os.makedirs(user_settings_folder)

        server_folder = f"{user_settings_folder}/servers/{self.server_uid}"
        if not os.path.exists(server_folder):
            os.makedirs(server_folder)

        config = dict(
            name=login,
            access_token=token['access_token'],
            token_type=token['token_type']
        )

        if server_folder is not None:
            with open(f"{server_folder}/current_user.json", 'w+') as f:
                json.dump(config, f, indent=4)
        
        self._session.log_info(f'Connected to {self.server_name} server, {self.BASE_URL}')

        return True

    def log_out(self):
        self.CONFIG = {'headers': None}
        
        user_path = f"{self.user_settings_folder()}/servers/{self.server_uid}/current_user.json"
        if os.path.exists(user_path):
            os.remove(user_path)
        
        self._session.log_info('Logged out')

    def check_log_in(self):
        logged_in = True
        user_path = f"{self.user_settings_folder()}/servers/{self.server_uid}/current_user.json"
        
        try:
            f = open(user_path, "r")
        except IOError:
            logged_in = False
        else:
            config = json.load(f)
            self.CONFIG['headers'] = {
                'Authorization': 'Bearer {}'.format(config['access_token'])
            }
            f.close()

            test_command = self.api_get('/versions', json={})
            
            if test_command is None:
                logged_in = False
                self._session.log_error(f'Connection failed to {self.server_name} server, {self.BASE_URL}')
            elif 'detail' in test_command and (test_command['detail'] == "invalid-token" or test_command['detail'] == "expired-token"):
                logged_in = False
                self._session.log_error(f'Token expired for {self.server_name} server, {self.BASE_URL}')
            else:
                self.current_user = config['name']
            
            if not logged_in:
                self.CONFIG = {'headers': None}
                os.remove(user_path)

        if logged_in:
            self._session.log_info(f'Connected to {self.server_name} server, {self.BASE_URL}')

        return logged_in

    def check_site(self):
        # Fetch current site parameter
        self.current_site = self._settings.fetch_key('current_site')

        # Fetch sites on remote
        data = self.api_get('/sites', json={})

        # No sites are defined
        if data is None or len(data) == 0:
            return ('no_sites', None)

        # Check sites to which the user is assigned
        assign_sites = []
        for remote in data:
            if self.api_get(f'/site-check-has-user?site={remote["name"]}&user={self.current_user}', json={}) is True:
                assign_sites.append(remote['name'])

        # Don't know which site to check
        if self.current_site is None:
            return ('not_assigned', None) if len(assign_sites) == 0 else ('argument', assign_sites)

        # Get current site data
        site_data = [remote for remote in data if remote['name'] == self.current_site]

        # Site is unknown
        if len(site_data) == 0:
            return ('unknown', assign_sites)
        else:
            site_data = site_data[0]

        # Site is disabled
        if site_data['is_enabled'] is False:
            return ('disabled', assign_sites)

        # Site is archived
        if site_data['is_archived'] is True:
            return ('archived', assign_sites)

        # User is not assigned to site
        if self.current_site not in assign_sites:
            return ('assigned', assign_sites) if len(assign_sites) != 0 else ('not_assigned', None)
        
        # Site is valid, we update the parameter
        self.update_settings({'current_site': self.current_site})
        
        return ('valid', None)

    def fetch_user_name(self, uid):
        try:
            f = open(f"{self.user_settings_folder()}/servers/{uid}/current_user.json", "r")
        except IOError:
            return None
        else:
            config = json.load(f)
            f.close()
            return config['name']


    def fetch_servers(self):
        return self._servers.fetch_servers()
    
    def update_server(self, data, uid=None):
        return self._servers.update_server(data, uid)

    def remove_server(self, uid):
        self._servers.remove_server(uid)
              
        if self.server_uid == uid:
            self.log_out()
            os.remove(f"{self.user_settings_folder()}/current_host.json")
            self.BASE_URL = 'http://0.0.0.0:0000'
            self.server_uid = None

        server_folder = f"{self.user_settings_folder()}/servers/{uid}"
        if os.path.exists(server_folder):
            shutil.rmtree(server_folder)

    def update_servers_order(self, data):
        user_settings_folder = self.user_settings_folder()

        with open(f"{user_settings_folder}/user_servers_order.json", 'w+') as f:
            json.dump(dict(uid_list=data), f, indent=4)
    
    def fetch_project(self,name):
        # Get projects data
        data = self.api_get('/projects', json={})
        
        # Remove disable and archived projects
        data = [
            remote 
            for remote in data
            if remote['is_enabled']
            and remote['is_archived'] is False
        ]
        # Filter projects to which user and site are assigned
        data = [
            remote
            for remote in data
            if self.check_project_has_user(remote['name'])
            and self.check_project_has_site(remote['name'])
        ]

        #Get project by name
        data = [
            remote
            for remote in data
            if remote['name'] == name
        ]
        
        return self._projects.fetch_projects(data, self.server_uid)[0]
    
    def fetch_cached_projects(self):
        return self._projects.fetch_projects(None, self.server_uid)

    def fetch_projects(self):
        # Get projects data
        data = self.api_get('/projects', json={})
        
        # Remove disable and archived projects
        data = [
            remote 
            for remote in data
            if remote['is_enabled']
            and remote['is_archived'] is False
        ]
        # Filter projects to which user and site are assigned
        data = [
            remote
            for remote in data
            if self.check_project_has_user(remote['name'])
            and self.check_project_has_site(remote['name'])
        ]
        
        return self._projects.fetch_projects(data, self.server_uid)

    def check_project_has_site(self, project_name):
        return self.api_get(f'/project-check-has-site?project={project_name}&user={self.current_site}', json={})

    def check_project_has_user(self, project_name):
        return self.api_get(f'/project-check-has-user?project={project_name}&user={self.current_user}', json={})

    def update_project(self, uid, updated=None):
        data = self.api_get(f'/projects/{uid}', json={})
        return self._projects.update_project(data, updated)

    def get_server_from_project(self,name):
        return self._projects.get_server_from_project(name)
    
    def update_project_env(self, project_name, project_uid):        
        # Fetch python path
        python_status = self.fetch_python_path()
        if python_status is False:
            self._session.log_error(f'Python path is invalid. Specify a correct version in the global settings.')
            return None, None

        # Get user config
        data_resolve = self.api_get(f'/project-resolve?project={project_name}&site={self.current_site}&user={self.current_user}', json={})
        
        if data_resolve is None:
            self._session.log_error(f'Overseer API `project-resolve` returns None. Make sure the user are assigned to {project_name} project and {self.current_site} site.')
            return None, None

        data_resolve['extensions'] = sorted(data_resolve['extensions'], key=lambda x: x['name'])

        # Check for Python minimum version
        for name, value in data_resolve['env'].items():
            if name == 'PYTHON_MIN_VERSION':
                if Version(self._settings.fetch_key('python_version')) < Version(value):
                    self._session.log_error(f'Your Python version is below the minimum requirement which is {value} for this project. You can change the version in the settings if you have one installed.')
                    return None, None

        # Set env folder
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)
        if not os.path.exists(env_folder):
            os.makedirs(env_folder)
        
        toml_config_path = f"{env_folder}/pyproject.toml"

        # Prepare extensions (dependencies) list
        main_dependencies = {}
        extensions_dependencies = {}

        for extension in data_resolve['extensions']:
            if not extension['version']['is_enabled']:
                continue

            # Use correct dict depend on dependencies type
            deps_dict = None

            if 'main' in extension['categories']:
                deps_dict = main_dependencies
            else:
                deps_dict = extensions_dependencies
            
            version = extension['version']

            if version['service'] == "pypi":
                # Using a specific version
                version_number = re.search('(~=|={2}|!=|<=|>=|<|>)', version["pypi"])
                if version_number:
                    name_split = re.split(f'({version_number.group(0)})', version["pypi"])
                    
                    version_number = ''.join(name_split[1:])
                    name = re.sub('[._+]', '-', name_split[0])
                # Using any version
                else:
                    version_number = "*"
                    name = re.sub('[._+]', '-', version["pypi"])

                deps_dict[name] = {"version": version_number}
                
                if "--pre" in version["pip_deps"]:
                    deps_dict[name]["allow-prereleases"] = "true"
            
            elif version['service'] == "gitlab":
                if (
                    "libreflow.extensions" not in extension["name"]
                    and 'main' not in extension["categories"]
                ):
                    extension['name'] = f'libreflow.extensions.{extension["name"]}'

                name = re.sub('[._+]', '-', extension['name'])

                if version['url']:
                    deps_dict[name] = {"git": version['url']}
                else:
                    git_url = f'https://gitlab.com/{version["repo_group"]}/{version["repo_project"]}.git'
                    deps_dict[name] = {"git": git_url}
                
                if version['repo_ref_type'] == "branch":
                    deps_dict[name]["branch"] = version['repo_ref']
                elif version['repo_ref_type'] == "commit":
                    deps_dict[name]["rev"] = version['repo_ref']
            
            elif version['service'] == "gitlab-url":
                if (
                    "libreflow.extensions" not in extension["name"]
                    and 'main' not in extension["categories"]
                ):
                    extension['name'] = f'libreflow.extensions.{extension["name"]}'

                name = re.sub('[._+]', '-', extension['name'])
                deps_dict[name] = {"git": version['url']}
        
        # Check all major dependencies in config
        if all(value is not False for value in [
            main_dependencies.get('kabaret', False),
            main_dependencies.get('libreflow', False),
            any([key for key in main_dependencies.keys() if re.search('libreflow[-]{1}', key)])
        ]) is False:
            self._session.log_error('A major dependency is missing. Make sure you have kabaret, libreflow and a libreflow flow module in your project extensions.')
            return None, None


        update = True
        if not os.path.exists(toml_config_path):
            update = False

        else:
            data = toml.load(toml_config_path) 
            if not data.get('project'):
                self._session.log_info("Migrating poetry project to uv")
                self.uninstall_project(project_uid)
                update = False

        
        if not update :
            python_version=self._settings.fetch_key('python_version')
            # create toml
            subprocess.call([
                "uv","init", "--bare", 
                "--name", f"{project_name}-uv",
                "--author-from", "none", 
                "--python", f"{python_version}", 
                "--project",f"{env_folder}"
            ])
        
        else : 
            subprocess.call(["uv","cache","clean"])

            subprocess.call(['uv', 'lock', '--upgrade'])
        
        # process is the same whether it is the init or not :

        # add main dependecies
        for name,options in main_dependencies.items() :

            command = ["uv", "add"]

            git = options.get('git')
            if git:
                git.replace(".git", "")
                name += f" @ git+{options['git']}"

            command.extend([f"{name}","--no-sync", "--project", f"{env_folder}"])

            branch = options.get('branch')
            if branch:
                command.extend(["--branch", f"{branch}"])

            prereleases = options.get('allow-prereleases')
            if prereleases:
                command.extend(["--prerelease", "allow"])
            
            subprocess.call(command)
        
        # add extensions dependecies
        for name,options in extensions_dependencies.items() :

            command = ["uv", "add"]

            git = options.get('git')
            if git:
                git.replace(".git", "")
                name += f" @ git+{options['git']}"

            command.extend([f"{name}","--group", "extensions", "--no-sync", "--project", f"{env_folder}"])

            branch = options.get('branch')
            if branch:
                command.extend(["--branch", f"{branch}"])

            prereleases = options.get('allow-prereleases')
            if prereleases:
                command.extend(["--prerelease", "allow"])
            
            subprocess.call(command)
        
        # Remove extension dependencies no longer used :

        toml_data = toml.load(toml_config_path)

        if toml_data.get('dependency-groups'):
            toml_list = toml_data.get('dependency-groups').get('extensions')
            
            for ext_string in toml_list:
                ext_name = re.search(r"^[^=><~]*", ext_string).group()

                if ext_name not in extensions_dependencies.keys():
                    subprocess.call(["uv","remove", ext_name, "--no-sync", "--group", "extensions" ,"--project", f"{env_folder}"])

        
            

        # # Format for toml config
        # main_dependencies_string = """"""
        # for name, options in main_dependencies.items():
        #     main_dependencies_string += f"{name} = "
        #     if type(options) is not dict:
        #         main_dependencies_string += f'"{options}"\n'
        #     else:
        #         for i, (option_name, option_value) in enumerate(main_dependencies[name].items()):
        #             if i > 0:
        #                 if option_name == "allow-prereleases":
        #                     main_dependencies_string += ', {name} = {value}'.format(name=option_name, value=option_value)
        #                 else:
        #                     main_dependencies_string += ', {name} = "{value}"'.format(name=option_name, value=option_value)
        #             else:
        #                 main_dependencies_string += '{{ {name} = "{value}"'.format(name=option_name, value=option_value)
                    
        #             if i == len(main_dependencies[name].items())-1:
        #                 main_dependencies_string += ' }'
                    
        #         main_dependencies_string += "\n"
        
        # extensions_dependencies_string = """"""
        # if len(extensions_dependencies) > 0:
        #     for name, options in extensions_dependencies.items():
        #         extensions_dependencies_string += f"{name} = "
        #         if type(options) is not dict:
        #             extensions_dependencies_string += f'"{name}"\n'
        #         else:
        #             for i, (option_name, option_value) in enumerate(extensions_dependencies[name].items()):
        #                 if i > 0:
        #                     extensions_dependencies_string += ', {name} = "{value}"'.format(name=option_name, value=option_value)
        #                 else:
        #                     extensions_dependencies_string += '{{ {name} = "{value}"'.format(name=option_name, value=option_value)
                        
        #                 if i == len(extensions_dependencies[name].items())-1:
        #                     extensions_dependencies_string += ' }'
                        
        #             extensions_dependencies_string += "\n"
            
        # # Create toml content
        # toml_content = """
        #     [project]
        #     name = "{project_name}-uv"
        #     version = "0.1.0"
        #     description = ""
        #     authors = ["Les Fees Speciales <voeu@les-fees-speciales.coop>"]
        #     requires-python = "{python_version}"

        #     [tool.uv]
        #     default-groups="all"

        #     [dependency-groups]
        #     main = [{main_list}]
        #     extensions = [{extensions_list}]
            
        #     [build-system]
        #     requires = ["uv_build>=0.7.15,<0.8"]
        #     build-backend = "uv_build"
        # """.format(
        #     project_name=project_name,
        #     python_version=self._settings.fetch_key('python_version'),
        #     main_list=main_dependencies_string,
        #     extensions_list=extensions_dependencies_string
        # )
        
        # # Move current process to env folder
        # store_base_path = os.getcwd()
        # os.chdir(env_folder)

        # update = True
        # if not os.path.exists(toml_config_path):
        #     update = False

        # with open(toml_config_path, "w") as f:
        #     f.write(toml_content)
        #     f.close()

        # # If config exists, we use update command
        # if update:
        #     subprocess.call([self.python_path, "-m", "poetry", "-n", "cache", "clear", "pypi", "--all"])
        #     subprocess.call([self.python_path, "-m", "poetry", "env", "use", self.python_path])
        #     subprocess.call([self.python_path, "-m", "poetry", "update"])
        # # Or we make the first install
        # else:
        #     subprocess.call([self.python_path, "-m", "poetry", "env", "use", self.python_path])
        #     subprocess.call([self.python_path, "-m", "poetry", "install"])
        
        # os.chdir(store_base_path)

        return data_resolve, env_folder

    def update_project_exec(self, project_uid, data_resolve):
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)

        # Format Flow Extensions pattern
        # and fetch libreflow flow module name
        extensions = []
        flow_module_name = None

        for extension in data_resolve['extensions']:
            if 'extension' in extension['categories']:
                if "libreflow.extensions" not in extension["name"]:
                    extensions.append(f'libreflow.extensions.{extension["name"]}:install_extensions')
                else:
                    extensions.append(f'{extension["name"]}:install_extensions')
            
            if 'main' in extension['categories'] and 'libreflow.' in extension['name']:
                flow_module_name = f'{extension["name"]}.gui'
        
        # Raise an error if flow is unknown
        if flow_module_name is None:
            self._session.log_error('A major dependency is missing. Make sure you have kabaret, libreflow and a libreflow flow module in your project extensions.')
            return False

        # Format launch command with arguments
        cmd = [
            "uv",
            "run",
            "-m",
            flow_module_name,
            "--host",
            data_resolve['redis_url'],
            "--port",
            str(data_resolve['redis_port']),
            "--db",
            str(data_resolve['redis_db']),
            "--cluster",
            data_resolve['redis_cluster'],
            "--session",
            "libreflow",
            "--site",
            self.current_site,
            "--password",
            data_resolve['redis_password'],
            "--search-index-uri",
            data_resolve["mongo_url"],
        ]

        if extensions :
            cmd.insert(cmd.index('-m'), "--group")
            cmd.insert(cmd.index('-m'), "extensions")
        
        # Add redis replica arguments
        if data_resolve['env'].get("KABARET_READ_REPLICA_HOST"):
            cmd.insert(cmd.index('--db'), "--read_replica_host")
            cmd.insert(cmd.index('--read_replica_host')+1, data_resolve['env']['KABARET_READ_REPLICA_HOST'])
        if data_resolve['env'].get("KABARET_READ_REPLICA_PORT"):
            cmd.insert(cmd.index('--db'), "--read_replica_port")
            cmd.insert(cmd.index('--read_replica_port')+1, data_resolve['env']['KABARET_READ_REPLICA_PORT'])

        # Format exec paths
        exec_path = f"{env_folder}/libreflow"
        exec_path += ".bat" if platform.system() == "Windows" else ".sh"

        sync_exec_path = exec_path.replace('libreflow.', 'libreflow_sync.')
        jobs_exec_path = exec_path.replace('libreflow.', 'libreflow_jobs.')
        index_exec_path = exec_path.replace('libreflow.', 'libreflow_index.')
        request_exec_path = exec_path.replace('libreflow.', 'libreflow_request.')

        # Use correct comment symbol
        comment_symbol = '::' if platform.system() == "Windows" else '#'

        # Format project environment variables
        env_variables = []
        for name, value in data_resolve['env'].items():
            # Ignore unnecesary args
            if name in [
                "KABARET_READ_REPLICA_HOST",
                "KABARET_READ_REPLICA_PORT",
                "KABARET_JOBS_POOL_NAME",
                "PYTHON_MIN_VERSION"
            ]:
                continue
            if platform.system() == "Windows":
                env_variables.append(f'set {name}={value}')
            else:
                env_variables.append(f'export {name}="{value}"')

        # Format Kabaret Flow Extensions environment variable
        if len(extensions) > 0:
            if platform.system() == "Windows":
                extensions = f'set KABARET_FLOW_EXT_INSTALLERS={";".join(extensions)}'
            else:
                extensions = f'export KABARET_FLOW_EXT_INSTALLERS="{";".join(extensions)}"'

        # Get job pools
        pool_names = data_resolve['env'].get("KABARET_JOBS_POOL_NAME", "compositing")
        pool_var = "JOBS_POOL_NAMES"
        if platform.system() == "Windows":
            pool_prompt =  f'set {pool_var}={pool_names}\n'
            pool_prompt += f'set /p "{pool_var}=Pool(s) (default: {pool_names}): "'
        else:
            pool_prompt = f'{pool_var}="{pool_names}"\n'
            pool_prompt = f'read -p "Pool(s) (default: {pool_names}): {pool_var}"'

        # Write main executable
        with open(exec_path, 'w+') as f:
            if platform.system() == "Windows":
                cmd.append('\ntimeout 30')
                f.write(f'@echo off\nTitle Libreflow {data_resolve["name"]}\nchcp 1252\n\n')
            else:
                cmd.append('\nsleep 30')
            
            f.write(f'{comment_symbol} Project environment variables\n')
            f.write('\n'.join(env_variables))
            
            if isinstance(extensions, str):
                f.write(f'\n\n{comment_symbol} Flow extensions\n')
                f.write(extensions)
            
            f.write(f'\n\n{comment_symbol} Start command\n')
            f.write(' '.join(cmd))

        # Write sync executable
        with open(sync_exec_path, 'w+') as f:
            sync_cmd = cmd.copy()

            if platform.system() == "Windows":
                f.write(f'@echo off\nTitle Libreflow Sync {data_resolve["name"]}\nchcp 1252\n\n')
            
            f.write(f'{comment_symbol} Project environment variables\n')
            f.write('\n'.join(env_variables))
            
            sync_cmd[5] = 'libreflow.sync'
            sync_cmd.insert(sync_cmd.index('--session'), "--project")
            sync_cmd.insert(
                sync_cmd.index('--project')+1,
                data_resolve['env'].get("LF_PROJECT_NAME", data_resolve["name"])
            )
            
            f.write(f'\n\n{comment_symbol} Start command\n')
            f.write(' '.join(sync_cmd))

        # Write jobs executable
        with open(jobs_exec_path, 'w+') as f:
            jobs_cmd = cmd.copy()

            if platform.system() == "Windows":
                f.write(f'@echo off\nTitle Libreflow Jobs {data_resolve["name"]}\nchcp 1252\n\n')
            
            f.write(f'{comment_symbol} Project environment variables\n')
            f.write('\n'.join(env_variables))

            if isinstance(extensions, str):
                f.write(f'\n\n{comment_symbol} Flow extensions\n')
                f.write(extensions)

            f.write(f'\n\n{comment_symbol} Pool names\n')
            f.write(pool_prompt)

            jobs_cmd[5] = 'libreflow.jobs_node'
            jobs_cmd.insert(6, f"%{pool_var}%" if platform.system() == "Windows" else f"${pool_var}")
            del jobs_cmd[-3:]

            if platform.system() == "Windows":
                jobs_cmd.append('\npause')

            f.write(f'\n\n{comment_symbol} Start command\n')
            f.write(' '.join(jobs_cmd))

        # Write index executable
        with open(index_exec_path, 'w+') as f:
            index_cmd = cmd.copy()
            index_cmd.insert(len(index_cmd)-1, "--search-auto-indexing")

            if platform.system() == "Windows":
                f.write(f'@echo off\nTitle Libreflow Index {data_resolve["name"]}\nchcp 1252\n\n')
            
            f.write(f'{comment_symbol} Project environment variables\n')
            f.write('\n'.join(env_variables))
            
            if isinstance(extensions, str):
                f.write(f'\n\n{comment_symbol} Flow extensions\n')
                f.write(extensions)
            
            f.write(f'\n\n{comment_symbol} Start command\n')
            f.write(' '.join(index_cmd))

        # Write request executable if sync extension
        if any(["file_manager.synchronisation" in extension['name'] for extension in data_resolve['extensions']]):
            with open(request_exec_path, 'w+') as f:
                request_cmd = cmd.copy()

                if platform.system() == "Windows":
                    f.write(f'@echo off\nTitle Libreflow Request {data_resolve["name"]}\nchcp 1252\n\n')
                
                f.write(f'{comment_symbol} Project environment variables\n')
                f.write('\n'.join(env_variables))
                
                if isinstance(extensions, str):
                    f.write(f'\n\n{comment_symbol} Flow extensions\n')
                    f.write(extensions)
                
                request_cmd[5] = 'libreflow.extensions.file_manager.synchronisation.request_session'

                request_cmd.insert(request_cmd.index('--session'), "--project")
                request_cmd.insert(
                    request_cmd.index('--project')+1,
                    data_resolve['env'].get("LF_PROJECT_NAME", data_resolve["name"])
                )

                request_cmd.insert(request_cmd.index('--search-index-uri')+2, '--delay')
                request_cmd.insert(request_cmd.index('--delay')+1, '600')
                
                f.write(f'\n\n{comment_symbol} Start command\n')
                f.write(' '.join(request_cmd))

        return True

    def start_project(self, project_uid, data_resolve, exec_mode=None):
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)
        
        # Move current process to env folder
        store_base_path = os.getcwd()
        os.chdir(env_folder)
        
        # Define executable path
        exec_path = f"{env_folder}/libreflow"
        if exec_mode is not None:
            exec_path += f"_{exec_mode}"
        exec_path += ".bat" if platform.system() == "Windows" else ".sh"

        # Check if executable exists
        if not os.path.exists(exec_path):
            self._session.log_error('Libreflow executable do not exist. Start a reinstall process.')
            return False

        # Set Process View parameter if enabled
        if next(filter(lambda d: "LIBREFLOW_SHOW_PROCESS_VIEW" in d, (data_resolve["site_env"], data_resolve["env"])), None) is None:
            if platform.system() == "Windows":
                env_variable = 'set LIBREFLOW_SHOW_PROCESS_VIEW=True'
            else:
                env_variable = 'export LIBREFLOW_SHOW_PROCESS_VIEW="True"'

            with open(exec_path, 'r') as f:
                exec_content = f.read()
                has_env = True if 'LIBREFLOW_SHOW_PROCESS_VIEW' in exec_content else False

            with open(exec_path, 'r') as f:
                exec_lines = f.readlines()
                
                for i, line in enumerate(exec_lines):
                    if (
                        self._settings.fetch_key('show_process_view')
                        and has_env is False and 'Project environment variables' in line
                    ):
                        exec_lines[i] = exec_lines[i].strip() + f'\n{env_variable}\n'
                    elif (
                        self._settings.fetch_key('show_process_view') is False
                        and has_env and 'LIBREFLOW_SHOW_PROCESS_VIEW' in line
                    ):
                        exec_lines.pop(i)
            
            with open(exec_path, 'w') as f:
                f.seek(0)
                f.writelines(exec_lines)

        # Start with correct command

        subprocess.call(["uv","cache","clean"])

        if platform.system() == "Windows":
            subprocess.Popen(exec_path, creationflags=subprocess.CREATE_NEW_CONSOLE)

        elif platform.system() == "Linux":
            subprocess.Popen(('chmod', '+x', exec_path)) 
            subprocess.Popen(('gnome-terminal', f'--title="Libreflow {data_resolve["name"]}"', '--', exec_path))

        elif platform.system() == 'Darwin':
            from applescript import tell
            
            macCommand = f'cd {os.path.dirname(exec_path)}; sh {exec_path}'
            tell.app( 'Terminal', 'do script "' + macCommand + '"')

        else:
            self._session.log_error("OS %s not supported" % platform.system())
            return False
        
        # Back current process to base path
        os.chdir(store_base_path)

        return True

    def start_terminal(self, project_uid, exec_mode):
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)
        
        # Move current process to env folder
        store_base_path = os.getcwd()
        os.chdir(env_folder)

        # Define executable path
        if exec_mode == "terminal":
            command = f'cd {env_folder}'
        else:
            python_status = self.fetch_python_path()
            if python_status is False:
                self._session.log_error(f'Python path is invalid. Specify a correct version in the global settings.')
                return
            # command = f'{self.python_path} -m uv cache clean'

        # Start with correct command
        if platform.system() == "Windows":
            subprocess.Popen(
                f'cmd.exe {command}' if exec_mode == "terminal" else command,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        
        elif platform.system() == "Linux":           
            subprocess.Popen(('gnome-terminal', '--', command))
        
        elif platform.system() == 'Darwin':
            from applescript import tell           
            tell.app( 'Terminal', 'do script "' + command + '"')
        
        else:
            self._session.log_error("OS %s not supported" % platform.system())
        
        # Back current process to base path
        os.chdir(store_base_path)

    def check_env(self, project_uid, project_name):
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)
        
        # Fetch python path
        python_status = self.fetch_python_path()
        if python_status is False:
            self._session.log_error(f'Python path is invalid. Specify a correct version in the global settings.')
            return None

        # Move current process to env folder
        store_base_path = os.getcwd()
        os.chdir(env_folder)

        toml_config_path = f"{env_folder}/pyproject.toml"

        if not os.path.exists(toml_config_path):
            return False

        # If venv exists
        # env_info = subprocess.Popen(
        #     [self.python_path, "-m", "poetry", "env", "info"],
        #     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        #     universal_newlines=True
        # )
        # env_status = re.search("(Valid).*(True)", env_info.communicate()[0])

        # if env_status is None:
        #     return None
        # else:
        #     self._session.log_info(f'{project_name} env is valid.')
        
        # Check correct python version

        # with open(toml_config_path,"rb") as f:
        data = toml.load(toml_config_path)

        if not data.get('project'):
            return False

        vspec = SpecifierSet(data.get('project').get('requires-python'))

        if self._settings.fetch_key('python_version') not in vspec:
            return False
        else:
            self._session.log_info(f'{project_name} python version is correct.')

        # env_python_version = re.search(
        #     f"(Python).*({self._settings.fetch_key('python_version')})", env_info.communicate()[0]
        # )

        # if env_python_version is None:
        #     return False
        # else:
        #     self._session.log_info(f'{project_name} python version is correct.')
        

        if not self._session.offline:

            # If all dependencies are installed
            env_deps = subprocess.Popen(
                ["uv", "pip", "check"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True
            )

            deps_warning = re.search("not installed", env_deps.communicate()[1])


            # Return invalid status if no match or content in stderr
            if deps_warning is not None:
                return False
            else:
                self._session.log_info(f'{project_name} dependencies are up to date.')

        # Back current process to base path
        os.chdir(store_base_path)

        return True

    def check_exec(self, project_uid, exec_name):
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)

        exec_ext = ".bat" if platform.system() == "Windows" else ".sh"
        return True if os.path.exists(f'{env_folder}/libreflow_{exec_name}{exec_ext}') else False

    def uninstall_project(self, project_uid):
        env_folder = self.resolve_value(self._settings.fetch_key('install_dir'), project_uid)
        
        # Fetch python path
        python_status = self.fetch_python_path()
        if python_status is False:
            self._session.log_error(f'Python path is invalid. Specify a correct version in the global settings.')
            return

        # Move current process to env folder
        store_base_path = os.getcwd()
        os.chdir(env_folder)

        # Get env name
        env_info = subprocess.Popen(
            [self.python_path, "-m", "poetry", "env", "list"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True
        )
        env_name = None 
        r = re.search("([^\s]+)", env_info.communicate()[0])
        if r:
            env_name = r.group(0)

        # Remove poetry env
        if env_name and env_name != ".venv":
            subprocess.call([self.python_path, "-m", "poetry", "env", "remove", env_name])

        # Back current process to base path
        os.chdir(os.path.dirname(store_base_path))

        # Delete env folder
        shutil.rmtree(env_folder)


    def fetch_settings(self):
        return self._settings.fetch_settings()
    
    def update_settings(self, data):
        return self._settings.update_settings(data)
    
    def fetch_python_custom_paths(self):
        return self._settings.fetch_python_custom_paths()
    
    def update_python_custom_paths(self, data):
        return self._settings.update_python_custom_paths(data)

    def update_python_current_version(self):
        number = self.fetch_python_version(self._settings.fetch_key('python_path'))
        
        if number != self._settings.fetch_key('python_version'):
            self.update_settings(dict(python_version=number))

    def fetch_python_versions(self):
        versions = []

        if platform.system() == "Windows":
            # Fetch python paths
            list_paths = subprocess.Popen("py --list-paths", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            list_paths = list_paths.communicate()[0].decode().splitlines()
            for p in list_paths:
                path = p.split(' ')[-1]
                if path:
                    # Get exact python version number
                    version_number = self.fetch_python_version(path)
                    # Append python version to list
                    versions.append(dict(
                        version=version_number,
                        path=path
                    ))
        elif platform.system() == "Linux":
            # Fetch python paths
            list_paths = subprocess.Popen(['ls -1 --color=none /usr/bin/python*'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            list_paths = list_paths.communicate()[0].decode().split('\n')
            for path in list_paths:
                if path:
                    # Get exact python version number
                    version_number = self.fetch_python_version(path)
                    
                    # Check if python version is already added to list
                    added = False
                    for v in versions:
                        if v['version'] == version_number:
                            added = True
                            break
                    
                    # Append python version to list
                    if not added:
                        versions.append(dict(
                            version=version_number,
                            path=path
                        ))
        
        return sorted(versions, key=lambda d: d['version'])

    def fetch_python_version(self, path):
        version_number = None
        try:
            version_number = subprocess.Popen([path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output_stdout = version_number.communicate()[0].decode()
            output_stderr = version_number.communicate()[1].decode()

            version_number = re.findall(
                r'(?:(\d+\.(?:\d+\.)*\d+))', output_stdout if output_stderr == "" else output_stderr
            )[0]
        except IOError as e:
            return None
                
        return version_number

    def fetch_python_path(self):
        if shutil.which(self._settings.fetch_key('python_path')):
            self.python_path = self._settings.fetch_key('python_path')
            return True
        return False

    def fetch_advanced_mode(self):
        return self._settings.fetch_key('advanced_mode')

    def user_settings_folder(self):
        return os.path.join(pathlib.Path.home(), '.libreflow_launcher')

    def resolve_value(self, value, project={}):
        resolved = value.format(
            user_settings=self.user_settings_folder(),
            project_uid=project
        )

        return resolved
