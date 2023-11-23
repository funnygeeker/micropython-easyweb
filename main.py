import time
from libs.easynetwork import Client
from libs.easyweb import EasyWeb, render_template, send_file, make_response

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