[English (英语)](./README.md)

# micropython-easyweb
![EasyWeb](./web/EasyWeb_256px.png)
- 适用于 `Micropython` 的：Web Server 库，简单，易用，多功能，高兼容性

### 特点
- 尽可能模仿了 `Flask` 框架的风格
- 集成了常用的：GET 请求解析，表单解析，HTML渲染，文件发送等功能

### 使用说明
- 本项目一共有三个版本的文件，请根据实际需要进行选择：
- `thread`: `/libs/easyweb_thread.py` 使用多线程实现
- `asyncio`: `/libs/easyweb.py` 使用异步实现，具有较好的兼容性和可靠性
- `single`: `/libs/easyweb_thread.py` 使用单线程循环实现，具有较好的兼容性

### 兼容性
#### 已通过测试设备
- `ESP-01S`: `single`
- `ESP32-C3`: `single`, `thread`, `asyncio`


### 示例代码
```python
from libs.easyweb import EasyWeb

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
    print('Full_Path: ', request.full_path)
    return ew.render_template("/web/wifi.html")

# 发送文件
@ew.route('/easyweb.png')
def img(request):
    return ew.send_file("/web/EasyWeb_256px.png")

# 停止 EasyWeb
@ew.route('/stop')
def stop(request):
    ew.stop()

# 获取字符串
@ew.route('/user/<string>')
def welcome(request):
    return "<h1>Hello {}</h1>".format(request.match)

# 获取路径
@ew.route('/download/<path>')
def download(request):
    return "<h1>Download {}</h1>".format(request.match)

ew.run()
print('======END======')
```