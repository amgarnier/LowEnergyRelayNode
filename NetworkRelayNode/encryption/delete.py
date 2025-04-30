import ubluetooth
from machine import Pin
import machine
import utime

pin = Pin("LED", Pin.OUT)

class ble_advertiser_scanner:

    def __init__(
        self
    ):
        self._ble = ubluetooth.BLE()
        self._ble.active(True)
        self._ble.config(gap_name="BLE_MESH_OBSERVER")  # type: ignore
        self._ble.irq(self.ble_irq)

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
                # send test advertisment

        elif event == 6:
            # print("done")
            pin.toggle()

    def scan_full_time(self):
        print("run")
        while True:
            pin.toggle()
            self._ble.gap_scan(30)
            utime.sleep_ms(35)

    def scan_window(self):
	# to do create code to allow for scan windows on probability model
            try:
            except KeyboardInterrupt:
                break
        pin.off()
        return self, success
