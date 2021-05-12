"""
    服务端响应
"""

from socket import *

sock = socket()
sock.bind(('127.0.0.1', 52962))
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.listen(5)


print('Whiting for connect...')
conn, addr = sock.accept()
print('Connect from', addr)

data = conn.recv(4096)  # 接收http请求
print(data.decode())

# 响应格式  大字符串
html = '''
HTTP/1.1 200 ok  # 条件一: 必须以这个格式开头,或者 HTTP/1.1 404 Not Fount
# 响应头写不写都可以 

Hello World!  # 条件二: 隔一个空行, 空行后面就是发送的内容
'''

conn.send(html.encode())  # 发送响应给客户端 (浏览器)

conn.close()
sock.close()
