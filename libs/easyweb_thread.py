# Github: https://github.com/funnygeeker/micropython-easyweb
# Author: funnygeeker
# Licence: MIT
# Date: 2023/11/18
#
# 参考项目：
# https://github.com/maysrp/micropython_webconfig
#
# 参考资料：
# https://blog.csdn.net/wapecheng/article/details/93522153
# https://blog.csdn.net/qq_42482078/article/details/131514743

import socket
import _thread
import binascii
import ujson as json


def url_encode(url):
    """URL 编码"""
    hex_url = binascii.hexlify(url.encode('utf-8')).decode('utf-8')
    encoded_url = ''
    for i in range(0, len(hex_url), 2):
        encoded_url += '%' + hex_url[i:i + 2].upper()
    return encoded_url


def url_decode(encoded_url):
    """URL 解码"""
    if '%' not in encoded_url:
        return encoded_url
    blocks = encoded_url.split('%')
    decoded_url = blocks[0]
    buffer = ""
    for b in blocks[1:]:
        if len(b) == 2:
            buffer += b[:2]
        else:
            decoded_url += binascii.unhexlify(buffer + b[:2]).decode('utf-8')
            buffer = ""
            decoded_url += b[2:]
    if buffer:
        decoded_url += binascii.unhexlify(buffer).decode('utf-8')
    return decoded_url


class _Request:
    """
    表示 HTTP 请求的类

    Attributes:
        path (str): 请求路径
        data (bytes): 请求体
        method (str): 请求方法，例如 GET / POST
        headers (dict): 请求头
        protocol (str): HTTP 协议版本
        full_path (str): 完整路径

    Properties:
        url (str / None): 获取请求中的 URL
        json (dict / None): 解析请求中的 JSON
        host (str / None): 获取请求中的 Host
        args (dict / None): 解析请求中的参数
        form (dict / None): 解析请求中的表单

    Note:
        在解析数据时，如果出现异常，则返回 None。
    """
    path: str = ''
    '请求路径'
    data: bytes = b''
    '请求体'
    method: str = ""
    '请求方法，例如 GET, POST'
    headers: dict = {}
    '请求头 (字典)'
    protocol: str = ""
    'HTTP 协议版本'
    full_path: str = ""
    '完整路径'
    match: str = None
    '匹配的结果'

    def __init__(self):
        self._url = None
        self._args = None
        self._form = None
        self._json = None

    @property
    def url(self):
        """
        获取请求中的 URL

        Returns:
            str / None: 当成功解析 URL 时返回 URL 字符串，否则返回 None（程序出错）

        Examples:
            request.url
        """
        if self._url is None:
            host = self.host
            if host:
                self._url = "http://{}{}".format(host, self.full_path)
        return self._url

    @property
    def json(self):
        """
        解析请求中的 JSON

        Returns:
            dict / None: 当成功解析 JSON 时返回字典，否则返回 None（程序出错）

        Examples:
            request.json
        """
        if self._json is None:
            try:
                self._json = json.loads(self.data)
            except:
                pass
        return self._json

    @property
    def host(self):
        """
        获取请求中的 Host

        Returns:
            str / None: 当成功解析 Host 时返回 Host 字符串，否则返回 None

        Examples:
            request.host
        """
        return self.headers.get('Host')

    @property
    def args(self):
        """
        解析请求中的参数

        Returns:
            dict / None: 当成功解析参数时返回参数字典，否则返回 None（无法解析时或程序出错）

        Examples:
            request.args
        """
        if self._args is None:
            try:
                # 提取问号后面的部分
                query_str = self.full_path.split('?', 1)[-1].rstrip("&")
                if query_str:
                    args_list = query_str.split('&')  # 分割参数键值对
                    args = {}
                    # 解析参数键值对
                    for arg_pair in args_list:
                        key, value = arg_pair.split('=')
                        key = url_decode(key)
                        value = url_decode(value)
                        args[key] = value
                    self._args = args  # 缓存结果
            except:
                pass
        return self._args

    @property
    def form(self):
        """
        解析请求中的表单数据

        Returns:
            dict / None: 当成功解析表单数据时返回表单数据字典，否则返回 None（无法解析时或程序出错）

        Examples:
            request.form
        """
        if self._form is None:
            try:
                items = self.data.decode("utf-8").split("&")
                form = {}
                for _ in items:
                    k, v = _.split("=", 1)
                    if not v:
                        v = None
                    else:
                        v = url_decode(v)
                    form[k] = v
            except:
                return None
            self._form = form  # 缓存结果
        return self._form


class _HttpError(Exception):
    """
    表示 HTTP 错误的异常类。
    """
    pass


class EasyWeb:
    # HTTP 响应代码
    CODE_200 = b"HTTP/1.1 200 OK\r\n"
    CODE_404 = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\nError 404: Page not found."
    CODE_405 = b"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\nError 405: Method not allowed."
    # 文件类型对照
    FILE_TYPE = {
        "txt": "text/plain",
        "htm": "text/html",
        "html": "text/html",
        "css": "text/css",
        "csv": "text/csv",
        "js": "application/javascript",
        "xml": "application/xml",
        "xhtml": "application/xhtml+xml",
        "json": "application/json",
        "zip": "application/zip",
        "pdf": "application/pdf",
        "ts": "application/typescript",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "otf": "font/otf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "ico": "image/x-icon"
    }  # 其他: "application/octet-stream"

    def __init__(self, host="0.0.0.0", port=80):
        self.host = host
        '监听的 IP'
        self.port = port
        '监听的端口'
        self.routes = []
        '路由表'
        self.server = True
        '服务器状态'

    def route(self, path: str, methods: list = None):
        """
        用于添加路由处理的装饰器

        Args:
            path: 用于匹配请求路径的字符串
            methods: 允许的请求方法列表，默认为 ['POST', 'GET']

        Example:
            @app.route("/")
            def index(request):
                return "Hello, World!"

        Notes:
            另外支持使用 "/<string>" 和 ”/<path>“ 对末尾的字符串或者路径进行匹配，可以通过 request.match 获取匹配的结果
        """
        # 添加路由装饰器
        if methods is None:
            methods = ['POST', 'GET']

        def decorator(func):
            self.routes.append((path, func, methods))
            return func

        return decorator

    def run(self):
        """
        运行 Web 服务器
        创建并启动循环，在其中运行服务器，监听客户端请求。

        Note:
            当调用此方法后，服务器将运行并阻塞事件循环，直到使用 `Ctrl+C` 或者 `stop()` 等方式进行终止。
        """
        # 创建套接字并监听连接
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        # 循环处理连接
        while self.server:
            conn, addr = s.accept()
            _thread.start_new_thread(self.handle, (conn,))

    def handle(self, conn):
        """
        处理客户端的请求并生成对应的响应。

        Args:
            conn: 用于从客户端读取请求数据和发送响应的对象
        """
        request = _Request()
        conn.settimeout(3)
        try:
            raw = conn.readline()  # HTTP 请求方法，路径，协议版本
            raw = raw.decode('utf-8').split(" ")
            if len(raw) != 3:
                return
            raw[2] = raw[2].rstrip("\r\n")
            request.method, request.full_path, request.protocol = raw
            request.path = request.full_path.split('?', 1)[0]
            # 协议版本检查
            if request.protocol not in ("HTTP/1.0", "HTTP/1.1"):
                raise _HttpError(request.protocol, 505, "Version Not Supported")
            # 解析 HTTP 请求头
            while True:
                raw = conn.readline()  # 请求头参数：\r\n
                raw = raw.decode('utf-8').rstrip('\r\n').split(": ", 1)
                if len(raw) == 2:
                    k, v = raw
                    request.headers[k] = v
                elif len(raw) == 1:  # 请求头结束：\r\n\r\n
                    break
                else:
                    pass
            # 查找匹配路由
            for route_path, route_func, route_methods in self.routes:
                # 匹配路由 "/" 和 "/<string>" "/<path>"
                # 完全匹配
                if route_path.rstrip("/") == request.path.rstrip("/"):
                    request.match = None
                    match_succes = True
                # 匹配字符串
                elif route_path[-9:] == "/<string>" and route_path[:-9] == "/".join(
                        request.path.rstrip("/").split("/")[:-1]):
                    request.match = request.path[len(route_path[:-9]) + 1:]
                    match_succes = True
                # 匹配路径
                elif (route_path[-7:] == "/<path>" and
                      "/".join(request.path.rstrip("/").split("/")[:-1]).startswith(route_path[:-7]) and
                      request.path[len(route_path[:-7]) + 1:]):
                    request.match = request.path[len(route_path[:-7]) + 1:]
                    match_succes = True
                else:
                    match_succes = False
                if match_succes:  # 完全匹配，字符串匹配，路径匹配
                    if request.method in route_methods:  # 匹配到路由
                        # 获取请求体
                        size = int(request.headers.get("Content-Length", 0))
                        if size:
                            request.data = conn.read(size)
                        else:
                            request.data = None
                        # 调用路由处理函数并发送响应
                        response = route_func(request)  # str / None / yield
                        if type(response) is str or type(response) is bytes:
                            if type(response) is str:
                                response = response.encode("utf-8")
                            if b"\r\n" not in response:  # 不存在响应头时自动补充
                                response = self.CODE_200 + b"\r\n" + response
                            conn.sendall(response)
                        elif response:
                            n = True
                            for res in response:
                                if type(res) is str:
                                    res = res.encode("utf-8")
                                if n:
                                    if b"\r\n" not in res:  # 不存在响应头时自动补充
                                        res = self.CODE_200 + b"\r\n" + res
                                    n = False
                                conn.sendall(res)
                        else:
                            if self.server:
                                print("[WARN] EasyWEB: Response is None, This could be due to the function not having "
                                      "a return statement.")
                    else:
                        # 发送"方法不允许"响应
                        conn.sendall(self.CODE_405)
                    break
            else:
                # 发送"页面不存在"响应
                conn.sendall(self.CODE_404)
        except OSError:
            pass
        except Exception as e:
            print("[WARN] EasyWEB: {}".format(e))
        finally:
            # 关闭连接
            conn.close()

    def stop(self):
        """
        停止运行 EasyWeb Server
        """
        if self.server:
            self.server = None
            _thread.exit()

    def send_file(self, file, mimetype: str = None, as_attachment=False, attachment_filename=None):
        """
        发送文件给客户端

        Args:
            file: 要发送的文件的路径
            mimetype: 文件的 MIME 类型。如果未指定，EasyWeb 将尝试根据文件扩展名进行猜测
            as_attachment: 是否作为附件发送文件，作为附件时会被下载
            attachment_filename: 下载文件时向用户显示的文件名。如果未提供，将使用原始文件名

        Returns:
            包含 HTTP 200 OK 和 文件的二进制数据 的可迭代对象
        """
        head = "Content-Type: {}\r\n\r\n"
        if as_attachment:  # 作为附件发送文件
            if not attachment_filename:  # 下载文件时的文件名
                attachment_filename = file.split("/")[-1]
            head = 'Content-Type: {}\r\n' + 'Content-Disposition: attachment; filename="{}"\r\n\r\n'.format(
                attachment_filename)
        else:
            if mimetype is None:  # 自动识别文件的 MIME 类型
                mimetype = "application/octet-stream"
                e = file.split(".")
                if len(e) >= 2:
                    mimetype = self.FILE_TYPE.get(e[-1], "application/octet-stream")
        yield self.CODE_200 + head.format(mimetype).encode("utf-8")
        with open(file, "rb") as f:
            _file = True
            while _file:
                _file = f.read(1024)
                yield _file

    def render_template(self, file, **kwargs):
        """
        渲染模板

        Args:
            file: 要渲染的 html 模板路径
            **kwargs: 传递给函数的其他关键字参数，将在模板中用于渲染

        Returns:
            包含 HTTP 200 OK 和渲染后的 HTML 内容字符串 的可迭代对象
        """
        yield self.CODE_200 + b"Content-Type: text/html\r\n\r\n"
        with open(file, "r") as f:
            _file = True
            f_readline = f.readline
            while _file:
                _file = f_readline() + f_readline() + f_readline() + f_readline() + f_readline()  # 五行一组进行渲染
                for k, v in kwargs.items():  # 渲染参数
                    _file = _file.replace("{{{{{}}}}}".format(k), str(v))
                yield _file.encode("utf-8")
