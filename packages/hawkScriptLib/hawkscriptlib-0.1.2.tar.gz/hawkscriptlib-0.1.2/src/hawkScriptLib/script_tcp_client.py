import socket

class myHawkGUI_PLC_API():
    def __init__(self, host='127.0.0.1', port=10080):
        """
        初始化TCP客户端
        :param host: 服务器主机地址
        :param port: 服务器端口号
        """
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        """连接到服务器"""
        try:
            # 创建TCP socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 连接服务器
            self.client_socket.connect((self.host, self.port))
            print(f"connected {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"connect error: {e}")
            return False

    def send(self, data):
        """
        发送数据到服务器
        :param data: 要发送的数据（字符串或字节）
        :return: 发送的字节数
        """
        try:
            # 确保数据是字节类型
            if isinstance(data, str):
                data = data.encode('utf-8')
            return self.client_socket.send(data)
        except Exception as e:
            print(f"send error: {e}")
            return 0

    def receive(self, buffer_size=1024):
        """
        接收服务器数据
        :param buffer_size: 接收缓冲区大小
        :return: 接收到的字节数据
        """
        try:
            return self.client_socket.recv(buffer_size)
        except Exception as e:
            print(f"receive error: {e}")
            return b''

    def close(self):
        """关闭连接"""
        if self.client_socket:
            self.client_socket.close()
            print("connect close")

    def read_value(self,addr:int,addr_long:int):
        """
        读取 PLC 寄存器的值
        :param addr: PLC 寄存器的开始地址
        :param addr_long: 需要读取的地址长度
        :return:
        """
        send_data = "1,"+str(addr)+","+str(addr_long)
        self.send(send_data)
        rcv_data = self.receive()
        if len(rcv_data) >0:
            rcv_data_split = rcv_data.decode('utf-8').split(",")[:addr_long]
        else:
            rcv_data_split = rcv_data.decode('utf-8')
        return rcv_data_split

    def write_value(self, addr:int, values:list):
        """
        写 PLC 的寄存器值
        :param addr: PLC 寄存器开始地址
        :param values: 需要写入的 PLC 值的列表 (list)
        :return:
        """
        send_data = "2," + str(addr) + "," + str(len(values))
        for data in values:
            send_data = send_data + ","
            send_data = send_data + str(data)
        self.send(send_data)
        rcv_data = self.receive()
        if len(rcv_data) > 0:
            rcv_data_split = rcv_data.decode('utf-8').split(",")[:len(values)]
        else:
            rcv_data_split = rcv_data.decode('utf-8')
        return rcv_data_split


    def __enter__(self):
        """支持with上下文管理"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close()


# 使用示例
# if __name__ == "__main__":
#     # 使用上下文管理器自动管理连接
#     with myHawkGUI_PLC_API('127.0.0.1', 10080) as client:
#         if client.client_socket:
#             # 发送数据
#             # client.send("Hello, Server!")
#             print(client.read_value(250,2))
#             print(client.write_value(250, [200,201]))
#