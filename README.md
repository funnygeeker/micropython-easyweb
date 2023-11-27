[简体中文 (Chinese)](./README.ZH-CN.md)
# micropython-easyweb

![EasyWeb](./web/EasyWeb_256px.png)
- Web Server Library for Micropython: Easy to use, versatile, highly compatible

### Features
- Aims to mimic the style of the Flask framework as much as possible
- Integrates common functionalities such as GET request parameter parsing, form parsing, HTML rendering, file sending, cookie setting, cookie retrieval, dynamic routing, and more.

### Instructions
- There are three versions of the project files, please choose the one that suits your needs:
- `thread`: `/libs/easyweb_thread.py` - implemented with multithreading
- `asyncio`: `/libs/easyweb.py` - implemented with asynchronous support, provides better compatibility and reliability
- `single`: `/libs/easyweb_single.py` - implemented with a single thread loop, provides good compatibility

### Compatibility
#### Tested Devices
- `ESP-01S`: `single`
- `ESP32-C3`: `single`, `thread`, `asyncio`

### Sample Code
- Here we use [micropython-easynetwork](https://github.com/funnygeeker/micropython-easynetwork) as an example to connect to the local network (it can also work in AP mode, allowing other devices to connect to the development board).
```python
import time
from libs.easynetwork import Client
from libs.easyweb import EasyWeb, render_template, send_file, make_response

client = Client()
client.connect("ssid", "password")  # or client.connect("ssid", "")

while not client.isconnected():
    pass
print('IP Address: {}'.format(client.ifconfig()[0]))

ew = EasyWeb()  # Initialize EasyWeb

# Add routes
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

# Send file
@ew.route('/easyweb.png')
def img(request):
    # Try accessing /easyweb.png on the website
    return send_file("/web/EasyWeb_256px.png")

# Download file
@ew.route('/download')
def download(request):
    # Try accessing /easyweb.png on the website
    # as_attachment: Whether to send the file as an attachment, it will be downloaded when sent as an attachment
    # attachment_filename: The filename displayed to the user when downloading. If not provided, the original filename will be used
    return send_file("/web/EasyWeb_256px.png", as_attachment=True, attachment_filename='easyweb.png')

# Stop EasyWeb
@ew.route('/stop')
def stop(request):
    ew.stop()

# Get string
@ew.route('/user/<string>')
def user(request):
    # Try accessing /user/123456 on the website
    return "<h1>Hello {}</h1>".format(request.match)

# Get path
@ew.route('/path/<path>')
def path(request):
    # Try accessing /path/123/456 on the website
    return "<h1>Path {}</h1>".format(request.match)

# Render HTML
@ew.route('/time')
def the_time(request):
    # Access /time on the website and refresh the page a few times to observe the changes on the webpage
    return render_template("/web/time.html", time=time.time())

# Get and set Cookies
@ew.route('/cookie')
def cookie(request):
    # Access /cookie on the website and refresh the page a few times to observe the changes on the webpage
    response = make_response('<h2>Cookies: {}</h2>'.format(str(request.cookies)))
    response.set_cookie('cookie_name', 'cookie_value')
    return response

# Custom status code
@ew.route('/404')
def status_code(request):
    # Access /404 on the website, open the developer tools to observe the status code
    return '<h2>404 Not Found</h2>', 404

# Get and set Cookies, while customizing the status code
@ew.route('/cookie2')
def cookie2(request):
    # Access /cookie on the website and refresh the page a few times to observe the changes on the webpage
    response = make_response()  # You can also assign a value to response.data later instead of initializing it during initialization
    response.data = '<h2>Cookies: {}</h2></br><h2>404 Not Found</h2>'.format(str(request.cookies))
    response.set_cookie('cookie_name', 'cookie_value')
    return response, 404

# Get content in JSON format
@ew.route('/json')
def cookie2(request):
    # Access /json on the website
    return {'type': 'json', 'num': 123}

ew.run()
print('======END======')  # Access /stop
```