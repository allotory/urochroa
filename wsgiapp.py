# -*- coding: utf-8 -*-

# WSGI主要是对应用程序与服务器端的一些规定

# 1. 应用程序需要提供一个可调用的对象
# 该对象可以是一个函数；一个实现了__call__方法的类的实例；
# 或者是一个类，这时生成实例的过程就相当于调用这个类。

# 2. 可调用对象需要接收两个参数 environ（dict）, start_response（function）

# 3. 可调用对象需要返回一个可迭代的值（list）

def app(environ, start_response):
    """ 一个 WSGI 应用程序.
        创建了自己的应用程序:)
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]

    # 应用程序必须在第一次返回可迭代数据之前调用 start_response 方法。
    # 这是因为可迭代数据是返回数据的 body 部分，
    # 在它返回之前，需要使用 start_response 返回 response_headers 数据。
    start_response(status, response_headers)

    # 多数情况下，这个可迭代对象，都只有一个元素，这个元素包含了HTML内容。
    # 应用程序会把需要返回的数据放在缓冲区里，然后一次性发送出去。
    # 但是在有些情况下，数据太大了，无法一次性在内存中存储这些数据，
    # 所以就需要做成一个可迭代对象，每次迭代只发送一块数据。
    return ['Hello world from a simple WSGI application!\n']
