#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2011 Rodrigo Pinheiro Marques de Araujo
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import os
from glob import glob
from SimpleXMLRPCServer import SimpleXMLRPCServer


class Service(object):

    def __init__(self):
        self.app_repo = os.environ['SYMBIAN_PYTHON_APPS']

    def _get_app_name(self, filename):
        return os.path.basename(filename)[:-3] # remove .py

    def list_applications(self):
        files = glob( self.app_repo + "/*.py"  )
        apps = [ self._get_app_name(filename) for filename in files ]
        return apps

    def get_app(self, name):
        with file(os.path.join(self.app_repo, name + ".py")) as f:
            content = f.read()

        return content

    def hello(self):
        return "Hello"



s = SimpleXMLRPCServer(('0.0.0.0', 8000))
s.register_instance(Service())
s.serve_forever()

