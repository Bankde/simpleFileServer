#!/usr/bin/env python
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import os
import traceback

class myServer(BaseHTTPRequestHandler):
    def __init__(self, directory, *args):
        self.dir = directory
        BaseHTTPRequestHandler.__init__(self, *args)

    def _set_headers(self, code=200, type='text/html'):
        self.send_response(code)
        self.send_header('Content-type', type)
        self.end_headers()

    def _list_files(self, folder):
        s = folder.split("/")
        if len(s) > 0:
            back = "/".join(s[:-1])

        if folder == "":
            self.wfile.write("<font size=6>/</font><br>-----------------------<br><br>")
        else:
            self.wfile.write("<font size=5>"+folder+"</font><br>-----------------------<br><br>")

        if back == "":
            self.wfile.write("<font size=6><a href=\"/\">..</a></font><br>")
        else:
            self.wfile.write("<a href=\"" + back + "\">..</a><br>")
            
        files = os.listdir(self.dir + folder)
        for f in files:
            if os.path.isfile(self.dir + folder + "/" + f):
                self.wfile.write(f + "&nbsp;&nbsp;&nbsp;<u><a href=\"" + folder + "/" + f + "\">Download</a></u>&nbsp;&nbsp;&nbsp;<u><a href=\"" + folder + "/" + f + "?read\">Text</a></u><br>")
            else:
                self.wfile.write("<u><a href=\"" + folder + "/" + f + "\">" + f + "</a></u><br>")

    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        # print parsed_path
        # ParseResult(scheme='', netloc='', path='/test/hi', params='', query='a=b', fragment='')
        path = parsed_path.path
        while True:
            if len(path) != 0 and path[-1] == "/":
                path = path[:-1]
            else:
                break

        if path == "/index.html":
            path = ""

        if path == "":
            self._set_headers(200)
            self._list_files("")
        else:
            _input_path = self.dir + path
            file_path = os.path.normpath(_input_path)
            if not file_path.startswith(self.dir):
                file_path = self.dir
                path = ""

            # print("filepath is %s" % file_path)
            if os.path.islink(file_path):
                self._set_headers(404)
                self.wfile.write("Symlink not allowed")
            elif os.path.isdir(file_path):
                self._set_headers(200)
                self._list_files(path)
            elif os.path.isfile(file_path):
                if parsed_path.query == "read":
                    self._set_headers(200, "text/plain")
                else:
                    self._set_headers(200, "application/octet-stream")

                f = file(file_path, "r")
                for line in f:
                    self.wfile.write(line)
            else:
                self._set_headers(404)
                self.wfile.write("File not found")

def run(server_class=HTTPServer, handler_class=myServer, port=80, directory=None):
    if directory == None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
    else:
        dir_path = directory

    print("File browse directory: %s" % dir_path)

    def handler(*args):
        handler_class(dir_path, *args)

    server_address = ('', port)
    try:
        httpd = server_class(server_address, handler)
        print("Server starts...")
        httpd.serve_forever()
    except:
        print(traceback.format_exc())
        raise
    print("Server stopped.")

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    elif len(argv) == 3:
        run(port=int(argv[1]), directory=argv[2])
    else:
        run()
