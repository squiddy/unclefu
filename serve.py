#!/usr/bin/env python

"""
Simple webserver that provides map data and textures for the webgl application.

Accessing local files with JavaScript is possible in some browsers, but not
enabled by default. The server listens on the local interface only.
"""

import SimpleHTTPServer
import SocketServer

PORT = 8000

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("127.0.0.1", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()
