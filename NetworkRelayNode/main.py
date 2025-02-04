from src.advertiser import MeshAdvertisingBearer
from classes.network_pdu import NetworkPdu

# This is the documentation for the BLE Advertiser code the .start is the mesh advertiser running with the set probability model. The .alwayson() is testing the original advertiser that would advertise a message conitinously and is used for testing purposes

# Define a mesh message
mesh_message_bytes = bytearray.fromhex(
    "68e476b5579c980d0d730f94d7f3509df987bb417eb7c05f"
)
networkPDU = NetworkPdu(mesh_message_bytes)
print(networkPDU)
# Initialize MeshAdvertisingBearer
MAB = MeshAdvertisingBearer(
    total_time_before_success_ms=300_000,
    number_of_relays=2,
    block_size_ms=30,
    probability=0.97,
    network_pdu=networkPDU,
).start()

# to test full on set .start() to always on
