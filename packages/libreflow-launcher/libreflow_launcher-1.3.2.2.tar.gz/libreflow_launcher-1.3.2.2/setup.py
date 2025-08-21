import setuptools
import versioneer
import os
import platform

readme = os.path.normpath(os.path.join(__file__, '..', 'README.md'))
with open(readme, "r", encoding="utf-8") as fh:
    long_description = fh.read()

long_description += '\n\n'

changelog = os.path.normpath(os.path.join(__file__, '..', 'CHANGELOG.md'))
with open(changelog, "r", encoding="utf-8") as fh:
    long_description = fh.read()



requirements = ["pyside6", "qtpy", "poetry", "requests", "uv", "toml"]
if platform.system() == 'Darwin':
    requirements.extend(["applescript"])

setuptools.setup(
    cmdclass=versioneer.get_cmdclass(),
    name="libreflow_launcher", # Replace with your own username
    version=versioneer.get_version(),
    author="Valentin Braem",
    author_email="valentin.braem@les-fees-speciales.coop",
    description="Launcher for instances of Libreflow asset-manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/lfs.coop/libreflow/libreflow_launcher",
    license="LGPLv3+",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    keywords="kabaret kitsu gazu animation pipeline libreflow launcher lfs overseer asset-manager",
    install_requires=requirements,
    python_requires='>=3.7',
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    package_data={
        '': [
            "*.css",
            '*.png',
            '*.svg',
            '*.ttf',
            '*.json'
        ],
    },

)
