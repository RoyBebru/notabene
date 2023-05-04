# import html
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse, parse_qs, unquote_plus
import webbrowser

"""Based on https://parsiya.net/blog/2020-11-15-customizing-pythons-simplehttpserver/"""

class PageEngine(BaseHTTPRequestHandler):

    def do_GET(self):
        # print(f"GET detected: '{self.path}'!")

        # first we need to parse it
        parsed = urlparse(self.path)
        # get the query string
        query_string = parsed.query
        # get the request path, this new path does not have the query string
        path = parsed.path

        if path == '/':
            path = "/index.html"

        print(f"path='{path}'; query: '{unquote_plus(query_string)}'")

        # send 200 response
        self.send_response(200)

        self.send_header("Content-Encoding", "gzip")
        # self.send_header("Content-Type", "text/html")

        # send response headers
        self.end_headers()
        # send the body of the response

        name = "browser/" + path[1:] + ".gz"
        try:
            with open(name, "rb") as fh:
                self.wfile.write(fh.read())
        except (FileNotFoundError, KeyError) as e:
            print(str(e))

    def do_POST(self):
        # read the content-length header
        content_length = int(self.headers.get("Content-Length"))
        # read that many bytes from the body of the request
        body = self.rfile.read(content_length)
        body = unquote_plus(body.decode("utf-8"))

        print(f"Post BODY: '{body}'")

        value = parse_qs(body)
        # for k in value.keys():
        #     print(f"key={k}: val='{value[k][0]}'")
        print(f"command='{value['command'][0]}'")

        self.send_response(200)
        self.end_headers()
        # echo the body in the response
        self.wfile.write(bytes(body, "utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        """Do not print log"""
        return

PORT = 8888

try:
    httpd = HTTPServer(('localhost', PORT), PageEngine)
    webbrowser.open(f"http://localhost:{PORT}")
    httpd.serve_forever()
except (OSError, PermissionError, OverflowError, KeyboardInterrupt):
    pass

#Handler = http.server.SimpleHTTPRequestHandler
#try:
#    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
#        print("serving at port", PORT)
#        httpd.serve_forever()
#except (OSError, PermissionError, OverflowError, KeyboardInterrupt):
#    pass
