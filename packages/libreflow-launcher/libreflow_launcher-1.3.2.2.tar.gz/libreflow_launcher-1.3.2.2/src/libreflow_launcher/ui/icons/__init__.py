import os
import libreflow_launcher.resources as resources

root = os.path.dirname(__file__)
for folder in os.listdir(root):
    path = os.path.join(root, folder)

    if os.path.isdir(path):
        if folder != '__pycache__':
            resources.add_folder(f'icons.{folder}', path)
