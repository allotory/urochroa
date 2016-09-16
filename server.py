# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import os


# 处理请求并返回页面
class RequestHandler(BaseHTTPRequestHandler):

    # 页面模板
    Error_Page = '''
        <html>
            <head>
                <title>Error Page</title>
            </head>
            <body>
                <h1>Error accessing {path}</h1>
                <p>{message}</p>
            </body>
        </html>
    '''

    # 发送内容
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.wfile.write(content)

    # 处理请求
    def do_GET(self):
        try:
            # 文件完整路径
            full_path = os.getcwd() + self.path

            if not os.path.exists(full_path):
                # 文件路径不存在
                raise ServerException("'{0}' not found".format(self.path))
            elif os.path.isfile(full_path):
                # 路径是文件
                self.handle_file(full_path)
            else:
                # 路径为不知名对象
                raise ServerException("Unknow object '{0}'".format(self.path))

        except Exception as message:
            self.handle_error(message)

    # 处理文件
    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as message:
            message = "'{0}' cannot be read: {1}".format(self.path, message)
            self.handle_error(message)

    # 处理异常
    def handle_error(self, message):
        content = self.Error_Page.format(path=self.path, message=message)
        self.send_content(content, 404)


# 服务器内部错误异常类
class ServerException(Exception):
    pass

if __name__ == '__main__':
    server_address = ('', 7000)
    server = HTTPServer(server_address, RequestHandler)
    server.serve_forever()
