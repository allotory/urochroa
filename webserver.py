# -*- coding: utf-8 -*-

import socket
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys

# WSGI主要是对应用程序与服务器端的一些规定

# 1. 服务器设置应用程序需要的两个参数
# 2. 调用应用程序
# 3. 迭代访问应用程序返回的结果，并将其传回客户端

class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # 创建一个 TCP/IP Socket 
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )

        # 在杀死或重启服务器后，允许重用相同的地址
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 服务器绑定指定地址，bind 函数分配一个本地地址给 socket
        listen_socket.bind(server_address)
        # 服务器监听 socket
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # New client connection
            self.client_connection, client_address = listen_socket.accept()
            # Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            self.handle_one_request()

    def handle_one_request(self):
        # in Python 2, the method socket.recv() returns a string 
        # while in Python 3 the same method returns a bytes object.
        # so we need bytes decode to string
        self.request_data = request_data = self.client_connection.recv(1024).decode('utf-8')
        # Print formatted request data a la 'curl -v'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (self.request_method,  # GET
         self.path,            # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()

    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # 必要的 WSGI 变量
        env['wsgi.version']      = (1, 0)
        # 表示 url 的模式，例如 "https" 还是 "http"
        env['wsgi.url_scheme']   = 'http'
        # 输入流，HTTP请求的 body 部分可以从这里读取
        env['wsgi.input']        = StringIO(self.request_data)
        # 输出流，如果出现错误，可以写往这里
        env['wsgi.errors']       = sys.stderr
        # 如果应用程序对象可以被同一进程中的另一线程同时调用，这个值为True
        env['wsgi.multithread']  = False
        # 如果应用程序对象可以同时被另一个进程调用，这个值为True
        env['wsgi.multiprocess'] = False
        # 如果服务器希望应用程序对象在包含它的进程中只被调用一次，那么这个值为True
        env['wsgi.run_once']     = False

        # 必要的 CGI 变量
        #
        # HTTP 请求方法：GET
        env['REQUEST_METHOD']    = self.request_method
        # URL 路径除了起始部分后的剩余部分，用于找到相应的应用程序对象。
        # 如果请求的路径就是根路径，这个值为空字符串：/hello
        env['PATH_INFO']         = self.path
        # SERVER_NAME, SERVER_PORT 与 SCRIPT_NAME，PATH_INFO 共同构成完整的 URL，
        # 它们永远不会为空。但是，如果 HTTP_HOST 存在的话，当构建 URL 时，
        # HTTP_HOST优先于SERVER_NAME。
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

    # status：状态码，response_headers：header（list），exc_info：错误处理
    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            print(type(response))
            # type(data) ==> bytes/str, type(response) ==> str, 
            # and sendall function need a bytes type parameter
            # then response += data may raise TypeError: Can't convert 'bytes' object to str implicitly
            # so need to convert response type from str to bytes
            # and validate data's type for whether convert to bytes
            response = bytes(response, encoding='utf-8')

            print(type(response))
            for data in result:
                if isinstance(data, str):
                    data = bytes(data, encoding='utf-8')
                response += data
            # Print formatted response data a la 'curl -v'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()


SERVER_ADDRESS = (HOST, PORT) = '', 8888


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()