import socket
import struct
from com.ssl_vision_wrapper_pb2 import SSL_WrapperPacket

class MulticastClient:
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))

        mreq = struct.pack("4sl", socket.inet_aton(address), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def receive(self):
        return self.sock.recv(10240)
    

if __name__ == "__main__":
    client = MulticastClient("224.5.23.2", 10020)

    while True:
        data = client.receive()
        packet = SSL_WrapperPacket()
        packet.ParseFromString(data)
        for entry in packet.detection.robots_blue:
            print(entry.robot_id)
