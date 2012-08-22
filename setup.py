#!/usr/bin/python

from distutils.core import setup
from glob import glob

setup(name='wlantest',
        version='0.1',
        license='GPLv2',
        description='Automatic wireless testing for Connman',
        author='Maxence Viallon',
        author_email='mviallon@aldebaran-robotics.com',
        packages=['wlantest'],
        package_dir={'wlantest': 'src'},
        data_files=[('/etc/wlantest', glob('cfg/*.cfg')),
                    ('/etc/wlantest', ['initscript/dhcpd.conf'])],
        scripts=['wlantest']
    )
