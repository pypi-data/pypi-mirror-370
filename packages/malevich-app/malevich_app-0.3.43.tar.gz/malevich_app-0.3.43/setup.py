import os
import pathlib
import shutil
from setuptools import setup, find_packages

version = open('version').read().strip()
requirements = open('requirements.txt').read().split()
__cur_path = f"{pathlib.Path(__file__).parent.resolve()}{os.sep}"
shutil.copyfile(f"{__cur_path}version", f"{__cur_path}malevich_app{os.sep}version")
shutil.copyfile(f"{__cur_path}requirements.txt", f"{__cur_path}malevich_app{os.sep}requirements.txt")

__other_dir = f"{__cur_path}malevich_app{os.sep}other{os.sep}"
os.makedirs(__other_dir, exist_ok=True)
shutil.copyfile(f"{__cur_path}jls.py", f"{__other_dir}jls.py")
shutil.copyfile(f"{__cur_path}version", f"{__other_dir}version")
shutil.copyfile(f"{__cur_path}malevich_app{os.sep}export{os.sep}start.py", f"{__other_dir}start.py")
shutil.copytree(f"{__cur_path}malevich", f"{__other_dir}malevich", dirs_exist_ok=True)

setup(
    name='malevich_app',
    version=version,
    author="Andrew Pogrebnoj",
    author_email="andrew@malevich.ai",
    packages=find_packages(),
    package_data={
        'malevich_app': ['version', 'requirements.txt', 'other/*', 'other/malevich/*', 'other/malevich/square/*'],
    },
    data_files=[
        ('', ['jls.py', 'version']),
    ],
    include_package_data=True,
    install_requires=requirements,
)
