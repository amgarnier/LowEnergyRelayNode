from classes.network_pdu import NetworkPdu
import ubluetooth
import utime
from machine import Pin
from classes.prob_model import prob_model

# This relay node sends a message

pin = Pin("LED", Pin.OUT)
# This code is for the mesh advertisment it takes in the advertisment details that want to be sent and probability model data. It takes in the Network PDU which is a class that is responsible for creating a network pdu. As the BLE is advertising a network PDU. The network pdu is encomposed in a transport PDU which the network pdu class handles.

# The network pdu has a method to create the network message which takes the network message and converts it to the advertisment message. IT does this by combining the address, message, and network keys.


class MeshAdvertisingBearer:
    """
    A class to handle BLE mesh advertising using ubluetooth.

    Attributes:
        _INTERVAL_US (int): Advertising interval in microseconds.
        _total_time_before_success_ms (int): Total time before success in milliseconds.
        _network_pdu (NetworkPdu): Network PDU object.
        _number_of_relays (int): Number of relays.
        _block_size (int): Block size in milliseconds.
        _probability (float): Probability of sending blocks.
        _send_blocks (list[int]): List of send blocks.
        mab (ubluetooth.BLE): BLE object.
        _send_message (bytearray): Message to be sent.

    Methods:
        advertise(AD_PDU_HEX: bytearray):
            Advertises the given AD PDU hex data.

        start():
            Starts the advertising process based on the send blocks and flashes an LED.

        always_adv_test():
            Continuously advertises the message and toggles an LED.
    """

    _INTERVAL_US = 100

    def __init__(
        self,
        total_time_before_success_ms: int = 300_000,
        number_of_relays: int = 2,
        block_size_ms: int = 30,
        probability: float = 0.97,
        send_blocks: list[int] = [],
        network_pdu: NetworkPdu = NetworkPdu(),
    ):
        self._total_time_before_success_ms = total_time_before_success_ms
        self._network_pdu = network_pdu
        self._number_of_relays = number_of_relays
        self._block_size = block_size_ms
        self._probability = probability
        self._send_blocks = send_blocks
        self.mab = ubluetooth.BLE()
        self.mab.active(True)
        print(f"MAC Address: {self.mab.config('mac')}")
        self.mab.config(gap_name="MESH")  # type: ignore
        print(f"Gap Name: {self.mab.config('gap_name')}")
        self._send_message = bytearray(network_pdu.create_network_from_message())

        # build probability model
        self._send_blocks = prob_model(
            total_time_before_success_ms=self._total_time_before_success_ms,
            number_of_relays=self._number_of_relays,
            block_size_ms=self._block_size,
            probability=self._probability,
            send_blocks=self._send_blocks,
        ).create_send_blocks()
        self._network_pdu = network_pdu

    def advertise(self, AD_PDU_HEX: bytearray):
        """
        Advertises the given Advertising PDU (Protocol Data Unit) in hexadecimal format.

        Args:
            AD_PDU_HEX (bytearray): The Advertising PDU in hexadecimal format.

        Converts the hexadecimal PDU to bytes and uses the `gap_advertise` method
        of the `mab` object to start advertising with the specified interval and
        advertising data.
        """
        ad_pdu_bytes = bytes(AD_PDU_HEX)  # Convert hex to bytes (skip '0x')
        block_size = self._block_size
        self.mab.gap_advertise(interval_us=block_size, adv_data=ad_pdu_bytes)
        print("message sent")

    # assume we know keys and network keys already
    # step 1 send PBADV message at set interval depending on window size and total time the lasat user wants to receive the message and number of relays
    # step 2 flash LED when message is sent and stay on for 5 seconds
    # step 3 count number of messages sent over the time period and print and end of time period.

    def start(self):
        """
        Starts the BLE advertising process.

        This method sends the BLE advertisement message at intervals specified
        in the _send_blocks list. It toggles a pin before each advertisement
        and prints the message in hexadecimal format. If a KeyboardInterrupt
        is detected, the process is stopped. After sending all messages, the
        pin is turned off and the total number of messages sent is printed.

        Returns:
            self: The instance of the class.
        """
        print(self._send_message.hex())
        for time in self._send_blocks:
            try:
                pin.toggle()
                self.advertise(self._send_message)
                print(".")
                utime.sleep_ms(time)
            except KeyboardInterrupt:
                break
        pin.off()
        print(f"sent {len(self._send_blocks)} messages")
        return self

    def always_adv_test(self):
        print(self._send_message.hex())
        # print(self._network_pdu._network_pdu.hex())
        while True:
            self.mab.gap_advertise(30000, self._send_message)
            utime.sleep_ms(1000)
            print(".")
            pin.toggle()
        return self


if __name__ == "__main__":
    # Define a mesh message
    mesh_message_bytes = bytearray.fromhex(
        "68e476b5579c980d0d730f94d7f3509df987bb417eb7c05f"
    )
    networkPDU = NetworkPdu(mesh_message_bytes)
    # Initialize MeshAdvertisingBearer
    MAB = MeshAdvertisingBearer(
        total_time_before_success_ms=300_000,
        number_of_relays=2,
        block_size_ms=30,
        probability=0.97,
        network_pdu=networkPDU,
    ).start()

    print(MAB._send_blocks)
