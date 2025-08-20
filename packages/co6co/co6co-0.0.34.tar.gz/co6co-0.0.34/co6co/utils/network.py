import os
import socket
import struct
import time
import select
import subprocess
import platform


def check_port(host, port) -> tuple[bool, str]:
    """
    检查指定主机的指定端口是否开放。
    :param host: 主机名或IP地址。
    :param port: 端口号。
    :return: 一个元组，第一个元素为True表示开放，False表示不开放，第二个元素为错误信息或None。
    """
    try:
        # 创建一个 TCP 套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置超时时间
        sock.settimeout(2)
        # 尝试连接到指定的主机和端口
        result = sock.connect_ex((host, port))
        if result == 0:
            return True, None
        else:
            return False, "端口不开放或网络不通"

    except socket.gaierror as e:
        return False, e
    except socket.error as e:
        return False, e
    finally:
        # 关闭套接字
        sock.close()


def get_local_ip(isIpv6: bool = False):
    """
    获取本机 IP 地址
    return: str
        本机 IP  地址
    """
    try:
        # 创建一个UDP套接字
        sock = socket.socket(socket.AF_INET6 if isIpv6 else socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个公共的IP地址和端口，
        # 这不会发送任何数据，但是会为套接字分配一个本地地址
        sock.connect(("2001:4860:4860::8888" if isIpv6 else "8.8.8.8", 80))
        # 获取分配给套接字的本地IP地址
        local_ip = sock.getsockname()[0]
    finally:
        # 关闭套接字
        sock.close()
    return local_ip

# ping 主机


def _checksum(source_string: bytes):
    """计算校验和（内部使用）"""
    sum_val = 0
    max_count = (len(source_string) // 2) * 2
    count = 0
    while count < max_count:
        val = source_string[count + 1] * 256 + source_string[count]
        sum_val = sum_val + val
        sum_val = sum_val & 0xffffffff  # 保持在32位内
        count += 2

    if max_count < len(source_string):
        sum_val = sum_val + source_string[-1]
        sum_val = sum_val & 0xffffffff

    sum_val = (sum_val >> 16) + (sum_val & 0xffff)
    sum_val = sum_val + (sum_val >> 16)
    answer = ~sum_val
    answer = answer & 0xffff

    # 主机字节序转网络字节序
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def ping_host(host: str, timeout: int = 2, count: int = 2):
    """
    测试主机是否可达

    参数:
        host (str): 目标主机名或IP地址
        timeout (int): 超时时间(秒)
        count (int): 尝试次数

    返回:
        bool: 主机可达返回True,否则返回False
    """
    try:
        
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as my_socket:
            # 设置超时
            my_socket.settimeout(timeout)
            # 获取主机IP
            try:
                host_ip = socket.gethostbyname(host)
            except socket.gaierror:
                return False

            # 发送多个数据包尝试
            for i in range(count):
                # 构建ICMP包
                icmp_type = 8  # 请求回显
                icmp_code = 0
                icmp_checksum = 0
                icmp_id = os.getpid() & 0xFFFF  # 进程ID
                icmp_seq = i + 1
                icmp_payload = b'pingdata'  # 简单的 payload

                # 构建ICMP头部
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)

                # 计算校验和
                icmp_checksum = _checksum(icmp_header + icmp_payload)
                icmp_header = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)

                # 完整的ICMP包
                packet = icmp_header + icmp_payload

                # 发送数据包
                send_time = time.time()
                my_socket.sendto(packet, (host_ip, 1))

                # 等待响应
                ready = select.select([my_socket], [], [], timeout)
                if not ready[0]:
                    continue  # 超时，尝试下一次

                # 接收响应
                recv_packet, addr = my_socket.recvfrom(1024)

                # 解析IP头部和ICMP响应
                ip_header = recv_packet[:20]
                _, _, _, _, _, ip_ttl, _, _, _, _ = struct.unpack('!BBHHHBBHII', ip_header)

                icmp_header = recv_packet[20:28]
                icmp_type, _, _, icmp_recv_id, _ = struct.unpack('!BBHHH', icmp_header)

                # 验证响应是否匹配
                if icmp_type == 0 and icmp_recv_id == (os.getpid() & 0xFFFF):
                    return True  # 收到有效响应，返回True

            # 所有尝试都失败
            return False

    except socket.error:
        print(f"套接字错误: {e}")
        if "permission denied" in str(e).lower() or "权限" in str(e):
            print("需要管理员权限才能运行此程序")
        # 处理权限错误等
        return False        


def ping(ip_address, count=4):
    """
     ping指定的IP地址
    
    参数:
        ip_address (str): 要ping的IP地址
        count (int): ping的次数，默认4次
        
    返回:
        tuple: (是否成功, 输出结果)
    """
    # 根据操作系统确定ping命令的参数
    param = '-n' if platform.system().lower() == 'windows' else '-c' 
    # 构建ping命令
    command = ['ping', param, str(count), ip_address] 
    try:
        # 执行ping命令
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        return (True, output)
    except subprocess.CalledProcessError as e:
        return (False, e.output)