# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer


# 处理请求并返回页面
class RequestHandler(BaseHTTPRequestHandler):

    # 页面模板
    page = '''
        <html>
            <head>
                <title>test</title>
            </head>
            <body>
                <p>hello, web!</p>
            </body>
        </html>
    '''

    # 处理请求
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Lenght', str(len(self.page)))
        self.end_headers()
        self.wfile.write(self.page.encode(encoding='utf-8'))

if __name__ == '__main__':
    server_address = ('', 7000)
    server = HTTPServer(server_address, RequestHandler)
    server.serve_forever()
