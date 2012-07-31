#!/usr/bin/python

from distutils.core import setup
from glob import glob

setup(name='wlantest',
        version='0.1',
        description='Python script for ConnMan testing',
        author='Maxence Viallon',
        author_email='mviallon@aldebaran-robotics.com',
        packages=['wlantest'],
        package_dir={'wlantest': 'src'},
        data_files=[('/etc/wlantest', glob('cfg/*.cfg')),
                    ('/etc/init.d', ['initscript/wlantest.sh'])],
        scripts=['wlantest']
    )
