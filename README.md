[简体中文 (Chinese)](./README.ZH-CN.md)
# micropython-easyweb
![EasyWeb](./web/EasyWeb_256px.png)
- Web Server library for `Micropython`: Simple, easy-to-use, versatile, highly compatible

### Features
- Aims to mimic the style of the `Flask` framework as much as possible
- Integrates commonly used functionalities such as parsing GET requests, form parsing, HTML rendering, and file sending

### Usage Instructions
- There are three versions of files available in this project, please choose according to your specific needs:
- `thread`: `/libs/easyweb_thread.py` implemented using multi-threading
- `asyncio`: `/libs/easyweb.py` implemented using asynchronous programming, with good compatibility and reliability
- `single`: `/libs/easyweb_thread.py` implemented using single-threaded looping, with good compatibility

### Compatibility
#### Tested Devices
- `ESP-01S`: `single`
- `ESP32-C3`: `single`, `thread`, `asyncio`

### Example Code
```python
from libs.easyweb import EasyWeb

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
    print('Full_Path: ', request.full_path)
    return ew.render_template("/web/wifi.html")

# Send a file
@ew.route('/easyweb.png')
def img(request):
    return ew.send_file("/web/EasyWeb_256px.png")

# Stop EasyWeb
@ew.route('/stop')
def stop(request):
    ew.stop()

# Get a string
@ew.route('/user/<string>')
def welcome(request):
    return "<h1>Hello {}</h1>".format(request.match)

# Get a path
@ew.route('/download/<path>')
def download(request):
    return "<h1>Download {}</h1>".format(request.match)

ew.run()
print('======END======')
```