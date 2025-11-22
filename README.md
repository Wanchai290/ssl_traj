# SSL Trajectory demo

## Installation
Follow the Protobuf [installation docs](https://protobuf.dev/installation/) first,
get the gencode version <= 29.

Run:

```
pip install -r requirements.txt
bash generate_protobuf.sh
```

Note that `protoletariat` requires Protobuf Gencode version <= 29 to work at the time of writing (2025/07/01)

## Running
- Connect to a Wi-Fi network (whether it has Internet access or not)
- Open the grSim software
- Check in the bottom window that packets are correctly sent on the network (red errors should not appear)

You can now run algorithms with the grSim simulator.

## Warnings
If grSim is minimized, or on another desktop, it might stop sending packets.
Keep it in an active window when working with it.

grSim uses multicast packet over IPv4. When multiple clients are connected to it,
the network is responsible for copying the packets. If you are connected on a network
specifically designed to stop multicast packets, grSim will not work. You can share your
network connection with your phone to avoid this problem.