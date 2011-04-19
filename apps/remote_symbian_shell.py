#/usr/bin/python 
# -*- coding: iso-8859-1 -*- 

# Copyright 2007 Nilton Volpato <nilton dot volpato | gmail com> 
# Copyright 2011 Rodrigo Pinheiro Marques de Araújo <fenrrir | gmail com> 
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 

"A Remote Python Shell for Symbian Phone" 

import sys 

try:
    import btsocket as socket
    apid = socket.select_access_point()
    apo = socket.access_point(apid)
    socket.set_default_access_point(apo)
    apo.start()
except ImportError, error:
    import socket

from code import InteractiveConsole 

class FakeOutputFile(object): 
    def __init__(self): 
        self.connection = None

    def register(self, conn): 
        self.connection = conn 

    def write(self, data): 
        out = self.connection
        if hasattr(out, 'sendall'): 
            out.sendall(data) 
        else: 
            out.write(data) 

sys.stdout = FakeOutputFile() 
sys.stdout.register(sys.__stdout__) 
sys.stderr = FakeOutputFile() 
sys.stderr.register(sys.__stderr__) 

class Shell(InteractiveConsole): 
    def __init__(self, conn, addr, locals=None, filename='<console>'): 
        InteractiveConsole.__init__(self, locals, filename) 

        self.conn = conn 
        self.addr = addr 

        self.delimiter = '\n' 
        self.MAX_LENGTH = 16384 
        self.recv_buffer = '' 

    def run(self): 
        sys.stdout.register(self.conn) 
        sys.stderr.register(self.conn) 
        try: 
            self.interact() 
            #self.interact('Started new thread. Welcome!') 
        finally: 
            self.conn.close() 

    def write(self, data): 
        self.conn.sendall(data) 

    def raw_input(self, prompt=''): 
        self.write(prompt) 
        while 1: 
            while 1: 
                try: 
                    line, self.recv_buffer = self.recv_buffer.split(self.delimiter, 1) 
                except ValueError: 
                    if len(self.recv_buffer) > self.MAX_LENGTH: 
                        line, self.recv_buffer = self.recv_buffer, '' 
                        return line.rstrip('\n') 
                    break 
                else: 
                    # XXX : pensar mais sobre essa parte 
                    # (parece haver algo errado em algum caso muito especial) 
                    if len(line) > self.MAX_LENGTH: 
                        line, self.recv_buffer = self.recv_buffer, '' 
                        return line.rstrip('\n') 
                    return line.rstrip('\n') 
            data = self.conn.recv(1024) 
            data = data.replace('\r\n','\n').replace('\r','\n') 
            #print >> sys.__stdout__, repr(data) 
            if not data: 
                break 
            if data == '\x04': 
                raise EOFError() 
            self.recv_buffer += data 
        return '' 

def start_serving(host, port): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host,port)) 
    s.listen(1) 
    while 1: 
        try: 
            conn, addr = s.accept() 
            Shell(conn, addr).run() 
        except KeyboardInterrupt: 
            s.close() 
            raise SystemExit 


if __name__ == '__main__': 
    start_serving(apo.ip(), 42042) 

