#!/usr/bin/env python3
from pyvesync import VeSync
import socketserver
import http.server
import os
import json

PORT=8001
USERNAME=os.getenv('vesync_username')
PASSWORD=os.getenv('vesync_password')
DEBUG=os.getenv('debug')
POLLRATE=120
Handler = http.server.SimpleHTTPRequestHandler

class ReqHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            resp = get_metrics()
            self.send_response(200)
            self.send_header('Content-type','text/plain')
            self.end_headers()
            self.wfile.write(resp[1:].encode('utf-8'))

def get_metrics():
    resp = ""
    manager.update();
    for device in manager.fans:
        data = json.loads(device.displayJSON())
        name = data['Device Name'].replace(' ','_').lower()
        model = data['Model'].lower()
        del data['Device Name']
        del data['Model']
        for item in data:
            field = item.replace(' ','_').lower()+'{name="'+name+'", model="'+model+'"}'
            if isinstance(data[item], str):
                if ' ' in data[item]:
                    value = f"\"{data[item]}\""
                else:
                    value = data[item]
                if value == 'off':
                    value = 0
                elif value == 'on':
                    value = 1
            resp = resp + "\n" + field + " " + str(value)
    return resp

with socketserver.TCPServer(("", PORT), ReqHandler) as httpd:
    print("Starting on port", PORT)
    manager = VeSync(USERNAME, PASSWORD, None, DEBUG)
    manager.login()
    httpd.serve_forever()