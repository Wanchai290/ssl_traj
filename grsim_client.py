import time
from multicast_client import MulticastClient
from com.grSim_Packet_pb2 import grSim_Packet
from com.grSim_Commands_pb2 import grSim_Robot_Command


class GrSimClient:
    def __init__(self, address: str = "127.0.0.1", port: int = 20011):
        self.client = MulticastClient(address, port, listen=False)
        self.packet = grSim_Packet()

    def set_target(
        self, color: str, id: int, vel_x: float, vel_y: float, vel_rot: float
    ):
        self.packet.commands.isteamyellow = color == "yellow"
        self.packet.commands.timestamp = time.time()

        command = grSim_Robot_Command()
        command.id = id
        command.kickspeedx = 0.0
        command.kickspeedz = 0.0

        command.veltangent = vel_x *1000.0
        command.velnormal = vel_y *1000.0
        command.velangular = vel_rot

        command.spinner = False
        command.wheelsspeed = False
        command.wheel1 = 0.0
        command.wheel2 = 0.0
        command.wheel3 = 0.0
        command.wheel4 = 0.0
        self.packet.commands.robot_commands.append(command)

    def send(self):
        print(self.packet)
        self.client.send(self.packet.SerializeToString())
        self.packet = grSim_Packet()


if __name__ == "__main__":
    client = GrSimClient()

    while True:
        client.set_target("blue", 0, 1, 0, 0)
        client.send()
        time.sleep(10e-3)
