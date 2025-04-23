# 1.a assume device is proxied and provide security keys and network keys

# 1.b scan for message
# -> input should be window size in ms and total time to receive message in minutes
# <-output should be message received
# count number of messages receieved and print at end of time period

from src.proxied_device import ProxiedDevice
import ubluetooth
from classes.prob_model import prob_model
from machine import Pin
import utime
from src.advertiser_bearer import AdvertiserBearer
from src.network_observer import MessageCache, NetworkObserver
from classes.network_pdu import NetworkPdu
from src.network_bearer import NetworkLayerBearer
from src.advertiser import MeshAdvertisingBearer

pin = Pin("LED", Pin.OUT)

success = 0

# this is the advertiser scanner device. It takes in the probability model. The proxied device and details are brought into the scanner as it is the keys that are used to decrypt and verify the received messages.

# scanned message - > Advertismentbearer(verify ad_type and mesh type)-> NetworkObserver(verify nid, mic, decrypt, cache, deobfusicate, verify if local )-> NetworkBearer(create the message) -> advertise


class ble_advertiser_scanner:

    def __init__(
        self,
        total_time_before_success_ms: int = 300_000,
        number_of_relays: int = 2,
        block_size_ms: int = 30,
        probability: float = 0.97,
        send_blocks: list[int] = [],
        proxied_device=ProxiedDevice(),
    ):
        self._total_time_before_success_ms = total_time_before_success_ms
        self._number_of_relays = number_of_relays
        self._block_size = block_size_ms
        self._probability = probability
        self._send_blocks = send_blocks
        self._ble = ubluetooth.BLE()
        self._proxied_device = proxied_device
        self._ble.active(True)
        self._ble.config(gap_name="BLE_MESH_OBSERVER")  # type: ignore
        self._ble.irq(self.ble_irq)
        self._proxied_device = proxied_device
        self._advertiser_bearer = AdvertiserBearer()
        self._adv_message = bytearray()
        self._network_pdu = NetworkPdu()

        self._send_blocks = prob_model(
            total_time_before_success_ms=self._total_time_before_success_ms,
            number_of_relays=self._number_of_relays,
            block_size_ms=self._block_size,
            probability=self._probability,
            send_blocks=self._send_blocks,
        ).create_send_blocks()

        # create message cache
        self._message_cache = MessageCache()

    def ble_irq(self, event, data):
        if event == 5:
            # A single scan result.
            addr_type, addr, adv_type, rssi, adv_data = data
            # adv_type of 3 is for ADV_NONCONN_IND which is a non connectable advertisment
            if adv_type == 0 and addr_type == 0:
                self._adv_message = bytearray(
                    adv_data
                )  # set the advertisment into the adv message
                print("e=", end=" ")
                print("addr_type", end=" ")
                print(addr_type, end=" ")
                print("addr", end=" ")
                print(addr, end=" ")
                print("adv_type=", end=" ")
                print(adv_type, end="")
                print("rssi=", end=" ")
                print(rssi, end=" ")
                print("adv_data=", end=" ")
                print(bytes(adv_data).hex(), end=" ")
                print("a single scan result")

                # # verify the advertisment bearer
                self.network_advertiser()

    def scan_full_time(self):
        while True:
            self._ble.gap_scan(0)
            utime.sleep_ms(50)  # want to sleep between relay to not overload device

    def scan_window(self):
        for time in self._send_blocks:
            try:
                pin.toggle()
                self._ble.gap_scan(
                    self._block_size,
                )
                pin.toggle()
                print(".")
                utime.sleep_ms(time)
            except KeyboardInterrupt:
                break
        pin.off()
        return self, success

    def network_advertiser(self):
        """
        Handles the network advertising process.

        This method performs the following steps:
        1. Verifies the advertiser bearer.
        2. Sends the message to the network observer for verification.
        3. Converts the message to a new advertisement message.
        4. Optionally advertises the new message (currently commented out for the experiment).

        Returns:
            bool: True if the process completes successfully, False otherwise.

        Raises:
            Exception: If any step in the process fails, the exception is caught and logged. It will stop the processing of the message
        """
        try:
            self.advertiser_bearer()
            # if no error from the advertiser bearer send to network observer to verify
            self.network_observer()  # send to network observer and verify
            global success  # this just allows us to increment the succesful number of received messages and allows duplicates to be read as a success
            success = +1
            self.network_bearer()  # convert message to new adv message
            # self.advertise()  # advertise message un-comment to utilize function
            return True
        except Exception as e:
            print("This has failed *************")
            print(e)
            return False

    def advertiser_bearer(self):
        """
        Initializes the advertiser bearer with the advertisement message and proxied device.

        This method creates an instance of AdvertiserBearer using the provided advertisement
        message and proxied device. It then calls the verify method on the created
        AdvertiserBearer instance to ensure it is correctly set up.

        Attributes:
            self._adv_message (str): The advertisement message to be used by the advertiser bearer.
            self._proxied_device (Device): The device to be proxied by the advertiser bearer.
            self._advertiser_bearer (AdvertiserBearer): The created advertiser bearer instance.
        """
        # create the advertisment bearer with the advertisment message
        self._advertiser_bearer = AdvertiserBearer(
            adv_message=self._adv_message, proxied_device=self._proxied_device  # type: ignore
        )
        self._advertiser_bearer.verify()

    # runs if the advertiser does not have an exception
    def network_observer(self):
        """
        Observes the network and retrieves the network PDU.

        This method creates an instance of NetworkObserver with the proxied device
        and advertiser bearer. It then calls the observe method on the NetworkObserver
        instance, passing the message cache, to verify and return the network PDU.

        Returns:
            The network PDU after verification.
        """
        networkObserver = NetworkObserver(
            proxied_device=self._proxied_device,
            advertiser_bearer=self._advertiser_bearer,
        )
        self._network_pdu = networkObserver.observe(
            message_cache=self._message_cache
        )  # verify and then return the network pdu

    # 3 Send to NEtwork bearer to process
    # -> NetworkPDU and update values
    # -> Send to BLE Advertiser
    def network_bearer(self):
        """
        Creates an advertisement message for the network layer bearer.

        This method initializes the `_adv_message` attribute by creating an
        advertisement message using the `NetworkLayerBearer` class. The
        advertisement message is constructed with the `networkPDU` and
        `proxied_device` attributes.

        Returns:
            None
        """
        self._adv_message = NetworkLayerBearer(
            networkPDU=self._network_pdu, proxied_device=self._proxied_device
        ).create_adv_message()

    def advertise(self):
        """
        Starts the advertising process using the MeshAdvertisingBearer.

        This method initializes and starts the MeshAdvertisingBearer with the specified parameters:
        - total_time_before_success_ms: The total time in milliseconds before considering the advertising successful.
        - number_of_relays: The number of relay nodes to use.
        - block_size_ms: The size of each time block in milliseconds.
        - probability: The probability of successful message transmission.
        - network_pdu: The network protocol data unit to be advertised.
        - send_message: The message to be sent during advertising.

        Returns:
            None
        """
        MAB = MeshAdvertisingBearer(
            total_time_before_success_ms=300_000,
            number_of_relays=2,
            block_size_ms=30,
            probability=0.97,
            network_pdu=self._network_pdu,
            send_message=self._adv_message,
        ).start()


# 4 send to BLE advertiser to advertise message
# Advertise message

if __name__ == "__main__":
    proxied_device = ProxiedDevice(
        unicast_address=bytearray.fromhex("12345678"),
        iv_index=bytearray.fromhex("12345678"),
        nonce=bytearray.fromhex("008b0148352345000012345678"),
        network_key=bytearray.fromhex("7dd7364cd842ad18c17c2b820c84c3d6"),
    )

    # test for scan window

    ble_scanner = ble_advertiser_scanner(
        total_time_before_success_ms=300_000,
        number_of_relays=2,
        block_size_ms=30,
        probability=0.97,
        proxied_device=proxied_device,
    ).scan_window()

    print(f"This test has had a total of {success} succesfull reads ")

    # #test for always on
    # ble_scanner = ble_advertiser_scanner(
    #     total_time_before_success_ms=300_000,
    #     number_of_relays=2,
    #     block_size_ms=30,
    #     probability=0.97,
    #     proxied_device=proxied_device,
    # ).scan_full_time()
