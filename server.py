# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import os


# 路径不存在条件类
class Case_no_file(object):

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


# 路径是文件条件类
class Case_existing_file(object):

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handler_file(handler.full_path)


# 所有条件都不符合时默认处理类
class Case_always_fail(object):

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknow object '{0}'".format(handler.path))


# 根目录 index page 条件处理类
class Case_index_file(object):

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) \
            and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))


# 根目录不存在 index page 条件处理类
class Case_no_index_file(object):

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) \
            and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)


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

    Listing_Page = '''
        <html>
            <head>
                <title>List Page</title>
            </head>
            <body>
                <ul>{0}</ul>
            </body>
        </html>
    '''

    # 所有可能情况
    Cases = [
        Case_no_file(),
        Case_existing_file(),
        Case_index_file(),
        Case_no_index_file(),
        Case_always_fail()
    ]

    # 处理请求
    def do_GET(self):
        try:
            # 文件完整路径
            self.full_path = os.getcwd() + self.path

            for case in self.Cases:
                handler = case
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as message:
            self.handle_error(message)

    # 发送内容
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        if isinstance(content, str):
            content = content.encode('utf-8')
        self.wfile.write(content)

    # 处理文件
    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as message:
            message = "'{0}' cannot be read: {1}".format(self.path, message)
            self.handle_error(message)

    # 显示目录结构
    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)

        except OSError as message:
            msg = "'{0}' cannot be listed: {1}".format(self.path, message)
            self.handle_error(msg)

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
