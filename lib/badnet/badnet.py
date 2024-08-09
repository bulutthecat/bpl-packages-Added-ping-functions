# Copywrite (c) 2024 Kevin Dalli

import http.client
import urllib.parse
import socket
import ssl
import ftplib
import fcntl
import struct
import array

class HttpClient:
    def __init__(self, base_url):
        parsed_url = urllib.parse.urlparse(base_url)
        self.scheme = parsed_url.scheme
        self.host = parsed_url.netloc
        self.conn = None

        if self.scheme == 'https':
            self.conn = http.client.HTTPSConnection(self.host)
        else:
            self.conn = http.client.HTTPConnection(self.host)

    def get(self, path, headers=None):
        self.conn.request("GET", path, headers=headers)
        response = self.conn.getresponse()
        return response.status, response.read()

    def post(self, path, data=None, headers=None):
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        self.conn.request("POST", path, body=urllib.parse.urlencode(data), headers=headers)
        response = self.conn.getresponse()
        return response.status, response.read()

    def close(self):
        self.conn.close()


class SocketClient:
    def __init__(self, host, port, use_ssl=False):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if use_ssl:
            self.context = ssl.create_default_context()
            self.sock = self.context.wrap_socket(self.sock, server_hostname=self.host)

    def connect(self):
        self.sock.connect((self.host, self.port))

    def send(self, data):
        self.sock.sendall(data.encode())

    def receive(self, buffer_size=4096):
        return self.sock.recv(buffer_size).decode()

    def close(self):
        self.sock.close()


class FtpClient:
    def __init__(self, host, user='', passwd=''):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.ftp = ftplib.FTP(self.host)

    def login(self):
        self.ftp.login(user=self.user, passwd=self.passwd)

    def list_files(self, directory='.'):
        return self.ftp.nlst(directory)

    def upload_file(self, file_path, remote_path):
        with open(file_path, 'rb') as file:
            self.ftp.storbinary(f'STOR {remote_path}', file)

    def download_file(self, remote_path, file_path):
        with open(file_path, 'wb') as file:
            self.ftp.retrbinary(f'RETR {remote_path}', file.write)

    def close(self):
        self.ftp.quit()


# Example usage:
#if __name__ == "__main__":
#    # HTTP Client example
#    http_client = HttpClient('https://jsonplaceholder.typicode.com')
#    status, content = http_client.get('/todos/1')
#    print(f"Status: {status}, Content: {content.decode()}")
#    http_client.close()
#
#    # Socket Client example
#    socket_client = SocketClient('example.com', 80)
#    socket_client.connect()
#    socket_client.send("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
#    print(socket_client.receive())
#    socket_client.close()
#
#    # FTP Client example
#    ftp_client = FtpClient('ftp.dlptest.com')
#    ftp_client.login()
#    print("Files:", ftp_client.list_files())
#    ftp_client.upload_file('local_file.txt', 'remote_file.txt')
#    ftp_client.download_file('remote_file.txt', 'downloaded_file.txt')
#    ftp_client.close()

#
# BELOW IS THE INTERFACE RETRIVAL API
#

def get_interface_info(interface):
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Get the interface IP address
    ip_address = socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', interface[:15].encode('utf-8'))
    )[20:24])
    
    # Get the netmask
    netmask = socket.inet_ntoa(fcntl.ioctl(
        sock.fileno(),
        0x891b,  # SIOCGIFNETMASK
        struct.pack('256s', interface[:15].encode('utf-8'))
    )[20:24])
    
    # Get the MAC address
    mac_address = ':'.join(['%02x' % b for b in fcntl.ioctl(
        sock.fileno(),
        0x8927,  # SIOCGIFHWADDR
        struct.pack('256s', interface[:15].encode('utf-8'))
    )[18:24]])
    
    return {
        'interface': interface,
        'ip_address': ip_address,
        'netmask': netmask,
        'mac_address': mac_address
    }

def list_interfaces():
    interfaces = []
    max_possible = 128  # Arbitrary. Raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', b'\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tobytes()
    
    for i in range(0, outbytes, 40):
        name = namestr[i:i+16].split(b'\0', 1)[0].decode('utf-8')
        interfaces.append(name)
    
    return interfaces