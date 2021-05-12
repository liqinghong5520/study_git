"""
web 服务程序

    假定: 用户有一组网页,希望使用我们提供的类,
         快速搭建一个服务器,实现自己网页的展示浏览

    IO多路复用 和 http训练

发布到网上:
    1.租个服务器,(假设:公网IP-174.168.0.1)
    2.添加安全组,打开租赁界面: 名称/ID-安全组-入方向规则-添加规则-添加端口
    3.一个终端访问服务器, ssh root@174.168.0.1
    4.再开一个终端,把web程序复制过服务器
            scp 作业_Web_Server.py root@174.168.0.1:/root
      把html文件夹也复制过去,
            scp -r static root@174.168.0.1:/root
    5.在服务器运行web程序
    6.其他人就可以访问了

"""
from socket import *
from select import select
import re


class WebServer:
    def __init__(self, host='0.0.0.0', port=80, html=None):
        self.host = host
        self.port = port
        self.html = html
        # 做IO多路复用并发模型准备
        self.__rlist = []
        self.__wlist = []
        self.__xlist = []
        self.sock = socket()
        self.sock.setblocking(False)
        self.create_socket()  # 在自身属性下执行,(跟直接写在init里面一样意思,细分)
        self.bind()  # 在自身属性下执行,(跟直接写在init里面一样意思,每一个功能单独封装)

    def create_socket(self):  # 创建套接字
        self.sock = socket()
        self.sock.setblocking(False)  # 非阻塞
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 关闭马上退出端口

    def bind(self):  # 绑定套接字地址
        self.addrless = (self.host, self.port)  # 类的局部变量
        self.sock.bind(self.addrless)

    def handle(self, conn):
        data = conn.recv(1024)
        # GET /xx HTTP/1.1 , 使用正则提取请求内容
        content = re.match(r"[A-Z]+\s+(?P<info>/\S*)", data.decode())
        if content:
            info = content.group('info')  # '/' 或者 /xxx
            self.send_html(conn, info)
        else:
            print('连接断开')
            self.__rlist.remove(conn)
            conn.close()

    def send_html(self, conn, info):  # 响应浏览器请求,注意格式!!!
        if info == '/':
            file = self.html + '/index.html'
        else:
            file = self.html + info
        try:  # 尝试打开这个文件
            print("尝试打开这个文件,路径:", file)
            f = open(file, 'rb')  # 打开网页文件
        except:  # 出错执行这个
            print('文件打开失败')
            content = 'HTTP/1.1 404 Not Fount\r\n'
            content += 'Content-Type: text/html\r\n'
            content += '\r\n'
            content += 'why?'
            conn.send(content.encode())

        else:  # 否则执行这个--else(表互斥)
            print("文件打开成功")
            data = f.read()  # 读取
            content = 'HTTP/1.1 200 OK\r\n'
            content += 'Content-type: text/html\r\n'
            # 声明一下内容长度,不然超范围会卡死
            content += 'Content-length: %d\r\n' % len(data)
            content += '\r\n'
            content = content.encode() + data  # 最后这个是=,不是+=
            conn.send(content)
            f.close()


    def start(self):
        self.sock.listen(5)
        print('Listen the port:', self.port)
        self.__rlist.append(self.sock)  # 第一步:监听socket对象
        while True:
            rs, ws, xs = select(self.__rlist, self.__wlist, self.__xlist)
            for r in rs:
                if r is self.sock:  # 有浏览器连接了,添加用户
                    conn, addr = r.accept()
                    # conn不能加self,不然就是类里面的全局变量了,会一直覆盖
                    print('Connect from:', addr)
                    conn.setblocking(False)
                    self.__rlist.append(conn)  # 第二步:监听connect对象
                else:  # 接收用户消息
                    try:
                        self.handle(r)
                    except:
                        self.__rlist.remove(r)
                        r.close()


if __name__ == '__main__':
    httpd = WebServer('127.0.0.1', 52961, './static')  # 创建一个类对象
    httpd.start()
