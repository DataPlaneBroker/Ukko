#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from osmclient import client
import logging
import json

vnf = dict()

def scale_vnf():
	cl = client.Client(host='localhost', sol005=True)
	print(cl.ns.scale_vnf("idb", "4", "apache_autoscale", False, True, False ))

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\n", str(self.path))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        global vnf
        print("*")
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        data = json.loads(json.loads(post_data.decode('utf-8')))

        vnf_name = data["notify_details"]["vdu_name"]
        print(vnf_name + " " + str(vnf.get(vnf_name, "undef")))
        if vnf_name in vnf:
            if vnf[vnf_name]["status"] == 'ok' and data['notify_details']['status'] == 'insufficient-data':
                print(data)
                print("scaling relay " + vnf_name + "...")
                scale_vnf()
            vnf[vnf_name]['status'] = data['notify_details']['status']
            vnf[vnf_name]['count'] = 0
        else:
            print(data)
            vnf[vnf_name] = {'status': data['notify_details']['status'], 'count': 0}

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
