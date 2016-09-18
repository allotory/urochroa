# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess


# 条件处理基类
class Base_case(object):

    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'


# 路径不存在条件类
class Case_no_file(Base_case):

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


# 路径是文件条件类
class Case_existing_file(Base_case):

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


# 所有条件都不符合时默认处理类
class Case_always_fail(Base_case):

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknow object '{0}'".format(handler.path))


# 根目录 index page 条件处理类
class Case_index_file(Base_case):

    def test(self, handler):
        return os.path.isdir(handler.full_path) \
            and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


# 根目录不存在 index page 条件处理类
class Case_no_index_file(Base_case):

    # 显示目录结构
    def list_dir(self, handler):
        try:
            entries = os.listdir(handler.full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = handler.Listing_Page.format('\n'.join(bullets))
            handler.send_content(page)

        except OSError as message:
            msg = "'{0}' cannot be listed: {1}".format(handler.path, message)
            handler.handle_error(msg)

    def test(self, handler):
        return os.path.isdir(handler.full_path) \
            and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.list_dir(handler.full_path)


# CGI
class Case_cgi_file(Base_case):

    def run_cgi(self, handler):
        data = subprocess.check_output(["python", handler.full_path])
        handler.send_content(data)

    def test(self, handler):
        return os.path.isfile(handler.full_path) \
            and handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)


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
        Case_cgi_file(),
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
