from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse
import webbrowser

"""Based on https://parsiya.net/blog/2020-11-15-customizing-pythons-simplehttpserver/"""

class MyHandler(BaseHTTPRequestHandler):
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
        print(f"query_string: '{query_string}'\npath={path}")

        # send 200 response
        self.send_response(200)
        # send response headers
        self.end_headers()
        # send the body of the response

        try:
            with open("-" + path, "rb") as fh:
                # self.wfile.write(bytes("<html><body bgcolor='gray'><h1>It Works!</h1></body></html>", "utf-8"))
                # self.wfile.write(bytes(fh.read(), "utf-8"))
                self.wfile.write(fh.read())
        except FileNotFoundError as e:
            print(e.strerror)

    def do_POST(self):
        # read the content-length header
        content_length = int(self.headers.get("Content-Length"))
        # read that many bytes from the body of the request
        body = self.rfile.read(content_length)

        self.send_response(200)
        self.end_headers()
        # echo the body in the response
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        """Do not print log"""
        return
        # print(format);
        # for arg in args:
        #     print(arg)
        # return
        # Output:
        # "%s" %s %s
        # GET /dhgsjshgajsdgja HTTP/1.1
        # 200
        # -

PORT = 8888

try:
    httpd = HTTPServer(('localhost', PORT), MyHandler)
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
