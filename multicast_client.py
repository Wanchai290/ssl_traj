import socket
import struct


class MulticastClient:
    def __init__(self, address: str, port: int, listen: bool = True):
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)

        if listen:
            self.sock.bind(("", port))

            mreq = struct.pack("4sl", socket.inet_aton(address), socket.INADDR_ANY)
            self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def receive(self):
        return self.sock.recv(10240)

    def send(self, data: bytes):
        self.sock.sendto(data, (self.address, self.port))


if __name__ == "__main__":
    client = MulticastClient("224.5.23.2", 10020)

    while True:
        data = client.receive()
        print(data)
