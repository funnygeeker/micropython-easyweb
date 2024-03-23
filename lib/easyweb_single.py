# Github: https://github.com/funnygeeker/micropython-easyweb
# Author: funnygeeker
# Licence: MIT
# Date: 2023/11/23
#
# 参考项目：
# https://github.com/maysrp/micropython_webconfig
#
# 参考资料：
# https://blog.csdn.net/wapecheng/article/details/93522153
# https://blog.csdn.net/qq_42482078/article/details/131514743
# https://blog.csdn.net/weixin_41665106/article/details/105599235
import os
import socket
import binascii
import ujson as json

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


def exists(path):
    """文件是否存在"""
    try:
        os.stat(path)
        return True
    except:
        print('[ERROR] EasyWeb: File Not Exists - {}'.format(path))
        return False


def url_encode(url):
    """URL 编码"""
    encoded_url = ''
    for char in url:
        if char.isalpha() or char.isdigit() or char in ('-', '.', '_', '~'):
            encoded_url += char
        else:
            encoded_url += '%' + binascii.hexlify(char.encode('utf-8')).decode('utf-8').upper()
    return encoded_url


def url_decode(encoded_url):
    """
    URL 解码
    """
    encoded_url = encoded_url.replace('+', ' ')
    # 如果 URL 中不包含'%', 则表示已解码，直接返回原始 URL
    if '%' not in encoded_url:
        return encoded_url
    blocks = encoded_url.split('%')  # 以 '%' 分割 URL
    decoded_url = blocks[0]  # 初始化解码后的 URL
    buffer = ""  # 初始化缓冲区

    for b in blocks[1:]:
        if len(b) == 2:
            buffer += b[:2]  # 如果是两位的十六进制数，加入缓冲区
        else:  # 解码相应的十六进制数并将其解码的字符加入解码后的 URL 中
            decoded_url += binascii.unhexlify(buffer + b[:2]).decode('utf-8')
            buffer = ""  # 清空缓冲区
            decoded_url += b[2:]  # 将剩余部分直接加入解码后的 URL 中
    # 处理缓冲区尾部剩余的十六进制数
    if buffer:
        decoded_url += binascii.unhexlify(buffer).decode('utf-8')
    return decoded_url  # 返回解码后的 URL


class _Response:
    """
    表示 HTTP 响应的类
    """
    STATUS_CODE = {
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        510: "Not Extended",
        511: "Network Authentication Required"
    }

    def __init__(self):
        self.status_code = 200
        'HTTP 状态码'
        self.status = None
        'HTTP 状态文本'
        self.headers = {}
        self.cookies = {}
        self.charset = 'utf-8'
        self.data = b''

    def set_data(self, data):
        """
        设置响应体数据

        Args:
            data: 数据，可以为 str, bytes, generator[bytes]
        """
        if isinstance(data, str):
            self.data = data.encode()

    def set_cookie(self, name: str, value: str = '', max_age: int = None):
        """
        构造包含提供的 cookies 和 max_age（可选）的 Set-Cookie 响应头

        参数:
            cookies: 包含 Cookie 键值对的字典。
            max_age: Cookie 最大有效期，以秒为单位。默认 None

        返回:
            bytes: Set-Cookie 响应头
        """
        if max_age is None:
            max_age = ""
        else:
            max_age = "; Max-Age={}".format(max_age)
        self.cookies[name] = "Set-Cookie: {}={}{}".format(url_encode(name), url_encode(value), max_age)

    @staticmethod
    def _generator():
        """一个生成器"""
        yield 0

    def is_generator(self, obj):
        """判断对象是否为生成器"""
        return isinstance(obj, type(self._generator()))

    def _get_status(self):
        """获取状态码"""
        if self.status is not None:
            return self.status
        else:
            return "{} {}".format(self.status_code, self.STATUS_CODE.get(self.status_code, "NULL"))

    def _get_cookies(self):
        """获取 Cookies"""
        c = ""
        for k, v in self.cookies.items():
            c += v
            c += "\r\n"
        return c

    def get_response(self):
        """
        获取完整的 HTTP 响应生成器

        Returns:
            包含响应内容的生成器
        """
        status = self._get_status()

        if isinstance(self.data, str):  # 处理数据
            self.data = self.data.encode()
            self.headers['Content-Type'] = 'text/html'
        elif isinstance(self.data, dict):
            self.data = json.dumps(self.data).encode()
            self.headers['Content-Type'] = 'application/json'
        else:
            self.data = self.data

        if isinstance(status, bytes):  # 响应头
            yield b"HTTP/1.1 " + status + b"\r\n"
        else:
            yield "HTTP/1.1 {}\r\n".format(status).encode()
        if isinstance(self.data, bytes):
            yield ("\r\n".join([f"{k}: {v}" for k, v in self.headers.items()]) + "\r\n").encode()
            yield (self._get_cookies() + "\r\n").encode()
            if self.data:
                yield self.data
        elif self.is_generator(self.data):
            i = True
            for d in self.data:
                if i:  # 只执行一次
                    i = False
                    if type(d) == dict:
                        self.headers.update(d)
                    yield ("\r\n".join([f"{k}: {v}" for k, v in self.headers.items()]) + "\r\n").encode()
                    yield (self._get_cookies() + "\r\n").encode()
                    if type(d) != dict:
                        yield d
                else:
                    yield d
        else:
            print("[WARN] EasyWeb: Unsupported data type.")


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

    def __init__(self):
        self._url = None
        self._args = None
        self._form = None
        self._json = None
        self._cookies = {}
        self.path: str = ''
        '请求路径'
        self.data: bytes = b''
        '请求体'
        self.method: str = ""
        '请求方法，例如 GET, POST'
        self.headers: dict = {}
        '请求头 (字典)'
        self.protocol: str = ""
        'HTTP 协议版本'
        self.full_path: str = ""
        '完整路径'
        self.match: str = None
        '匹配的结果'

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

    @property
    def cookies(self):
        """
        解析请求中的 Cookie 数据

        Returns:
            dict / None: 当成功解析 Cookies 数据时返回 Cookies 数据字典，否则返回 None（无法解析时或程序出错）

        Examples:
            request.cookies
        """
        if not self._cookies:
            try:
                cookies = {}
                items = self.headers.get('Cookie').split(";")
                for item in items:
                    item = item.strip()
                    if '=' in item:
                        k, v = item.split('=', 1)
                        k = url_decode(k)
                        v = url_decode(v)
                        cookies[k] = v
            except:
                return {}
            self._cookies = cookies  # 缓存结果
        return self._cookies


class _HttpError(Exception):
    """
    表示 HTTP 错误的异常类。
    """
    pass


class EasyWeb:
    # HTTP 响应代码
    CODE_200 = b"HTTP/1.1 200 OK\r\n"
    CODE_404 = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h2>Error 404: Page not found.</h2>"
    CODE_405 = b"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n<h2>Error 405: Method not allowed.</h2>"

    def __init__(self):
        self.host = str
        '监听的 IP'
        self.port = int
        '监听的端口'
        self.routes = []
        '路由表'
        self.server = None
        '服务器实例'

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

    def run(self, host="0.0.0.0", port=80):
        """
        运行 Web 服务器
        创建并启动循环，在其中运行服务器，监听客户端请求。

        Note:
            当调用此方法后，服务器将运行并阻塞事件循环，直到使用 `Ctrl+C` 或者 `stop()` 等方式进行终止。
        """
        self.host = host
        '监听的 IP'
        self.port = port
        '监听的端口'
        self.server = True
        # 创建套接字并监听连接
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        # 循环处理连接
        while self.server:
            conn, addr = s.accept()
            self.handle(conn)

    def handle(self, conn):
        """
        处理客户端的请求并生成对应的响应。

        Args:
            conn: 用于从客户端读取请求数据和发送响应的对象
        """
        request = _Request()
        conn.settimeout(5)
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
                    match_success = True
                # 匹配字符串
                elif route_path[-9:] == "/<string>" and route_path[:-9] == "/".join(
                        request.path.rstrip("/").split("/")[:-1]):
                    request.match = request.path[len(route_path[:-9]) + 1:]
                    match_success = True
                # 匹配路径
                elif (route_path[-7:] == "/<path>" and
                      "/".join(request.path.rstrip("/").split("/")[:-1]).startswith(route_path[:-7]) and
                      request.path[len(route_path[:-7]) + 1:]):
                    request.match = request.path[len(route_path[:-7]) + 1:]
                    match_success = True
                else:
                    match_success = False
                if match_success:  # 完全匹配，字符串匹配，路径匹配
                    if request.method in route_methods:  # 匹配到路由
                        # 获取请求体
                        size = int(request.headers.get("Content-Length", 0))
                        if size:
                            request.data = conn.read(size)
                        else:
                            request.data = None
                        # 调用路由处理函数并发送响应
                        response = route_func(request)  # str / bytes / generator / None
                        try:
                            response.get_response
                        except AttributeError:
                            if isinstance(response, tuple):  # return response, status_code, headers
                                try:
                                    response[0].get_response
                                    status_code = response[1]
                                    if len(response) == 3:
                                        headers = response[2]
                                    else:
                                        headers = None
                                    response = response[0]
                                    response.status_code = status_code
                                    if headers:
                                        response.headers.update(headers)
                                except AttributeError:
                                    if len(response) == 2:
                                        response = make_response(response[0], response[1])
                                    elif len(response) == 3:
                                        response = make_response(response[0], response[1], response[2])
                            else:  # return bytes / str / iterables / tuple (bytes / str / iterables, status_code, headersr)
                                response = make_response(response)

                        for res in response.get_response():
                            conn.sendall(res)
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


def send_file(file, mimetype: str = None, as_attachment=False, attachment_filename=None):
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
    head = {'Content-Type': 'application/octet-stream'}
    if as_attachment:  # 作为附件发送文件
        if not attachment_filename:  # 下载文件时的文件名
            attachment_filename = file.split("/")[-1]
        head['Content-Disposition'] = 'attachment; filename="{}"'.format(attachment_filename)
    else:
        if mimetype is None:  # 自动识别文件的 MIME 类型
            e = file.split(".")
            if len(e) >= 2:
                head['Content-Type'] = FILE_TYPE.get(e[-1], "application/octet-stream")
    if not exists(file):
        yield {'Content-Type': 'text/html'}
        yield '<h2>File Not Exists: {}</h2>'.format(file).encode("utf-8")
    else:
        yield head
        with open(file, "rb") as f:
            _file = True
            while _file:
                _file = f.read(1024)
                yield _file


def render_template(file, **kwargs):
    """
    渲染模板

    Args:
        file: 要渲染的 html 模板路径
        **kwargs: 传递给函数的其他关键字参数，将在模板中用于渲染

    Returns:
        包含 HTTP 200 OK 和渲染后的 HTML 内容字符串 的可迭代对象
    """
    yield {'Content-Type': 'text/html'}
    if not exists(file):
        yield '<h2>File Not Exists: {}</h2>'.format(file).encode("utf-8")
    else:
        with open(file, "r") as f:
            _file = True
            f_readline = f.readline
            while _file:
                _file = f_readline() + f_readline() + f_readline() + f_readline() + f_readline()  # 五行一组进行渲染
                for k, v in kwargs.items():  # 渲染参数
                    _file = _file.replace("{{{{{}}}}}".format(k), str(v))
                yield _file.encode("utf-8")


def make_response(content=b'', status_code: int = 200, headers=None) -> _Response:
    """
    创建一个带有 内容、状态码 和 头部 的 响应对象。

    Args:
        content: 响应的内容，可以为 Iterable (bytes)，str，tuple，dict
        status_code (int): 响应的状态码，默认为 200。
        headers: 可选的头部，包含在响应中，默认为 None。

    Returns:
        _Response: 响应对象
    """
    if headers is None:
        headers = {}
    response = _Response()
    if isinstance(content, tuple):
        if len(content) >= 2:
            content, status_code = content[:2]
        if len(content) == 3:
            headers = content[2]
    response.headers = headers
    response.status_code = status_code
    response.data = content
    return response
