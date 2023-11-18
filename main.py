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
