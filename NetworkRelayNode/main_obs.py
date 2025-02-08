from src.proxied_device import ProxiedDevice
from src.advertiser_scanner import ble_advertiser_scanner

# This is the main class for the ble scanner that takes in a message.
# To work this has to take a proxied device to be able to read the data from the message.


proxied_device = ProxiedDevice(
    unicast_address=bytearray.fromhex("12345678"),
    iv_index=bytearray.fromhex("12345678"),
    nonce=bytearray.fromhex("008b0148352345000012345678"),
    network_key=bytearray.fromhex("7dd7364cd842ad18c17c2b820c84c3d6"),
)

# test for scan window

ble_scanner, success = ble_advertiser_scanner(
    total_time_before_success_ms=300_000,
    number_of_relays=1,
    block_size_ms=30,
    probability=0.97,
    proxied_device=proxied_device,
).scan_window()
