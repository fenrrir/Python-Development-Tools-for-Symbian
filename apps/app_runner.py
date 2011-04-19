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
import codecs
import appuifw
import btsocket
import xmlrpclib
import traceback


APP_SAVE_DIR = '/data/python'
RUNNER_DATABASE = '/app_runner.dat'


class App(object):

    def __init__(self):
        self.proxy = None
        self.apps = None
        self.require_network_setup = True
        self.wlan_connection = None
        self.servers = {}


    def add_server(self):
        address_port = appuifw.multi_query(u"Endereço IP:", u"Porta")

        if address_port:
            address, port = address_port

        port = port
        server_name = appuifw.query(u"Nome do Servidor",u"text")
        if address and port and server_name:
            self.servers[server_name] = dict(address=address,port=port)
            self.save_servers()
        
        self.home()
        

    def exit(self):
        if self.wlan_connection:
            self.wlan_connection.stop()


    def home(self):
        user_input = appuifw.popup_menu([u"Connectar", u"Adicionar Servidor"], u"Conexão")
        if user_input is None:
            self.exit()
            return

        self.read_servers()
        if user_input == 0:
            self.select_server()
        else:
            self.add_server()


    def select_server(self):
        servers = list(self.servers)
        index = appuifw.selection_list(servers)
        if not index is None:
            server_conf = self.servers[ servers[index] ]
            self.connect( server_conf['address'], server_conf['port'])
            self.list_apps()
        else:
            self.home()


    def connect(self, address, port):

        if self.require_network_setup:
            apid = btsocket.select_access_point()
            self.wlan_connection = btsocket.access_point(apid)
            btsocket.set_default_access_point(self.wlan_connection)
            self.wlan_connection.start()
            self.require_network_setup = False

        self.proxy = xmlrpclib.ServerProxy("http://%s:%s" % (address, port))


    def list_apps(self):
        if self.apps is None:
            self.apps = [ unicode(app) for app in self.proxy.list_applications() ]

        if len(self.apps) == 0:
            appuifw.note(u"Não existem apps no servidor", u"error")
            return

        index = appuifw.selection_list(self.apps)
        if not index is None:
            self.run_app( self.apps[index] )
        else:
            self.select_server()



    def run_app(self, name):
        code = self.proxy.get_app(name)

        lines = code.split('\n')
        if 'coding' in lines[0]:
            run_code = "\n".join(lines[1:])
        else:
            run_code = code

        exec run_code
        self.save(name, code)
        self.list_apps()



    def save(self, app_name, code):

        filename = APP_SAVE_DIR + '/' + app_name + '.py'

        yes = appuifw.popup_menu([u"Não", u"Sim"], u"Salvar?")
        if not yes:
            return

        if os.path.exists(filename):
            yes = appuifw.popup_menu([u"Não", u"Sim"],u"Sobrescrever?")
            if not yes:
                return

        try:
            f = codecs.open(filename, 'w', 'UTF-8')
            f.write(code)
            f.close()
        except IOError, error:
            traceback.print_exc()
            appuifw.note(u"Erro ao salvar", u'error')
            return

        appuifw.note(u"Salvo com sucesso")
        self.list_apps()


    def save_servers(self):
        f = codecs.open(RUNNER_DATABASE, 'w', 'UTF-8')

        for server, server_data in self.servers.items():
            content = "%s %s %s" % (server, server_data['address'], server_data['port'])
            f.write(content + "\n")

        f.close()


    def read_servers(self):
        if self.servers:
            return 

        if os.path.exists(RUNNER_DATABASE):
            f = codecs.open(RUNNER_DATABASE, encoding='UTF-8')
            for line in f:
                try:
                    name, address, port = line.split()
                    self.servers[name] = { "address" : address, "port" : port }
                except ValueError, error:
                    pass
        else:
            appuifw.note(u'Insira um servidor',u'error')
            self.add_server(self)


    def run(self):
        self.home()



def main():
    App().run()


main()

