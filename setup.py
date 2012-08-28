#!/usr/bin/python
###
##  Automatic wireless testing for Connman
##
##  Copyright (C) 2012-2013  Aldebaran Robotics. All rights reserved.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License version 2 as
##  published by the Free Software Foundation.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from distutils.core import setup
from glob import glob

setup(name='wlantest',
        version='1.0',
        license='GPLv2',
        description='Automatic wireless testing for Connman',
        author='Aldebaran Robotics',
        author_email='mviallon@aldebaran-robotics.com',
        packages=['wlantest'],
        package_dir={'wlantest': 'src'},
        data_files=[('/etc/wlantest/cfg', glob('cfg/*.cfg')),
                    ('/etc/wlantest', ['src/main.conf'])],
        scripts=['wlantest']
    )
