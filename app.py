import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        recieve = self.path.split('/')
        data_to_send = recieve[1]
        protocol = recieve[2]
        url = None
        if protocol == "tcp":
            url = "http://localhost:20139"
            subprocess.Popen(['python3', 'server_tcp.py'])
        else:
            url = "http://localhost:20139"
            arg1 = data_to_send
            subprocess.Popen(['python3', 'server_rudp.py', arg1])
        self.send_response(302)
        self.send_header("127.0.0.1", url+"/"+data_to_send+"/"+protocol)
        self.end_headers()

if __name__ == "__main__":
    server_address = ("", 30701)
    httpd = HTTPServer(server_address, RedirectHandler)
    print("Server application started on port 30701...")
    httpd.serve_forever()

