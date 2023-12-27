[English (英语)](./README.md)

# micropython-easyweb
![EasyWeb](./web/EasyWeb_256px.png)
- 适用于 `Micropython` 的：简易 Web Server 库，易用，多功能

### 特点
- 尽可能模仿了 `Flask` 框架的风格
- 集成了常用的：GET 请求参数解析，表单解析，HTML渲染，文件发送，Cookies设置，Cookies获取，动态路由 等常用功能

### 使用说明
- 本项目一共有三个版本的文件，请根据实际需要进行选择：
- `thread`: `/lib/easyweb_thread.py` 使用多线程实现
- `asyncio`: `/lib/easyweb.py` 使用异步实现，具有较好的兼容性和可靠性
- `single`: `/lib/easyweb_single.py` 使用单线程循环实现，具有较好的兼容性

### 兼容性
#### 已通过测试设备
- `ESP-01S`: `single`
- `ESP32-C3`: `single`, `thread`, `asyncio`


### 示例代码
- 这里我们使用 [micropython-easynetwork](https://github.com/funnygeeker/micropython-easynetwork) 作为示例，连接局域网（也可以工作在AP模式，使用其他设备连接开发板）
```python
import time
from lib.easynetwork import Client
from lib.easyweb import EasyWeb, render_template, send_file, make_response

client = Client()
client.connect("ssid", "password")  # 或者 client.connect("ssid", "")

while not client.isconnected():
    pass
print('IP Address: {}'.format(client.ifconfig()[0]))

ew = EasyWeb()  # 初始化 EasyWeb

# 添加路由
@ew.route('/')
def home(request):
    print("=======[request]=======")
    print('URL: ', request.url)
    print('Args: ', request.args)
    print('Form: ', request.form)
    print('Host: ', request.host)
    print('Json: ', request.json)
    print('Path: ', request.path)
    print('Header: ', request.headers)
    print('Cookies: ', request.cookies)
    print('Full_Path: ', request.full_path)
    return render_template("/web/wifi.html")

# 发送文件
@ew.route('/easyweb.png')
def img(request):
    # 访问网页的 /easyweb.png 试试？
    return send_file("/web/EasyWeb_256px.png")

# 下载文件
@ew.route('/download')
def download(request):
    # 访问网页的 /easyweb.png 试试？
    # as_attachment: 是否作为附件发送文件，作为附件时会被下载
    # attachment_filename: 下载文件时向用户显示的文件名。如果未提供，将使用原始文件名
    return send_file("/web/EasyWeb_256px.png", as_attachment=True, attachment_filename='easyweb.png')

# 停止 EasyWeb
@ew.route('/stop')
def stop(request):
    ew.stop()

# 获取字符串
@ew.route('/user/<string>')
def user(request):
    # 访问网页的 /user/123456 试试？
    return "<h1>Hello {}</h1>".format(request.match)

# 获取路径
@ew.route('/path/<path>')
def path(request):
    # 访问网页的 /path/123/456 试试？
    return "<h1>Path {}</h1>".format(request.match)

# 渲染 HTML
@ew.route('/time')
def the_time(request):
    # 访问网页的 /time 然后刷新几遍页面，观察网页的变化
    return render_template("/web/time.html", time=time.time())

# 获取与设置 Cookies
@ew.route('/cookie')
def cookie(request):
    # 访问网页的 /cookie 然后刷新几遍页面，观察网页的变化
    response = make_response('<h2>Cookies: {}</h2>'.format(str(request.cookies)))
    response.set_cookie('cookie_name', 'cookie_value')
    return response

# 自定义状态码
@ew.route('/404')
def status_code(request):
    # 访问网页的 /404，打开开发人员工具观察状态码
    return '<h2>404 Not Found</h2>', 404

# 获取与设置 Cookies，同时自定义状态码
@ew.route('/cookie2')
def cookie2(request):
    # 访问网页的 /cookie 然后刷新几遍页面，观察网页的变化
    response = make_response()  # 也可以在后面为 response.data 赋值，来代替初始化时赋值
    response.data = '<h2>Cookies: {}</h2></br><h2>404 Not Found</h2>'.format(str(request.cookies))
    response.set_cookie('cookie_name', 'cookie_value')
    return response, 404

# 获取 JSON 格式的内容
@ew.route('/json')
def cookie2(request):
    # 访问网页的 /json
    return {'type': 'json', 'num': 123}

ew.run()
print('======END======')  # 访问 /stop
```