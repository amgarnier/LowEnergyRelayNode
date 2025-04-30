from classes.network_pdu import PbAdvertisingBearer, AdvBearerMessagePdu, NetworkPdu

import src.proxied_device as pd


##advertiser bearer class
class AdvertiserBearer:
    """
    A class to represent an Advertiser Bearer.

    Attributes
    ----------
    adv_message : bytearray
        The advertisement message.
    proxied_device : pd.ProxiedDevice
        The proxied device.

    Methods
    -------
    verify():
        Scans for advertisement messages and verifies their types.
    verify_ad_type():
        Verifies the advertisement type of the message.
    verify_mesh_ad_type():
        Verifies the mesh advertisement type of the message.
    """

    def __init__(
        self,
        adv_message: bytearray = bytearray(),
        proxied_device: pd.ProxiedDevice = pd.ProxiedDevice(),
    ):
        self._adv_message = adv_message
        self.proxied_device = proxied_device

    def verify(self):
        """
        Verifies advertisement messages by checking their types.

        This method scans for advertisement messages and verifies their types
        by calling `verify_ad_type` and `verify_mesh_ad_type` methods. If a
        ValueError is raised during the verification process, it catches the
        exception and prints the error message.

        Raises:
            ValueError: If the advertisement type or mesh advertisement type
                        is invalid.
        """
        # scan for adv messages
        try:
            self.verify_ad_type()
            self.verify_mesh_ad_type()
        except ValueError as e:
            print(e)

    def verify_ad_type(self):
        """
        Verifies the advertisement type (AD Type) of the advertisement message.

        This method checks if the second byte of the advertisement message
        corresponds to the expected AD Type value (0x20). If the AD Type is
        invalid, a ValueError is raised.

        Returns:
            self: The instance of the class if the AD Type is valid.

        Raises:
            ValueError: If the AD Type is not 0x20.
        """
        ad_type = self._adv_message[1].to_bytes(1, "big")
        if ad_type != bytearray.fromhex("20"):
            raise ValueError("Invalid AD Type")
        return self

    def verify_mesh_ad_type(self):
        """
        Verifies the Mesh AD Type in the advertisement message.

        This method checks if the third byte of the advertisement message
        corresponds to the expected Mesh AD Type (0x2a). If the type does not
        match, a ValueError is raised.d

        Returns:
            self: The instance of the class.

        Raises:
            ValueError: If the Mesh AD Type is invalid.
        """
        ad_mesh_type = self._adv_message[2].to_bytes(1, "big")
        if ad_mesh_type != bytearray.fromhex("2a"):
            raise ValueError("Invalid Mesh AD Type")
        return self


if __name__ == "__main__":

    # create the message as an example
    networkPdu = NetworkPdu(
        network_pdu_message=bytearray.fromhex(
            "68eca487516765b5e5bfdacbaf6cb7fb6bff871f035444ce83a670df"
        )
    )
    print(networkPdu._network_pdu)
    adv_bearer_pdu = AdvBearerMessagePdu(contents=networkPdu)
    pb_advertiser_bearer = PbAdvertisingBearer(contents=adv_bearer_pdu)
    proxied_device = pd.ProxiedDevice(
        unicast_address=bytearray.fromhex("70cf7c9732a345b691494810d2e9cbf4"),
        network_key=bytearray.fromhex("7dd7364cd842ad18c17c2b820c84c3d6"),
    )
    # or just scan and get the value:
    # "0x1e202a68eca487516765b5e5bfdacbaf6cb7fb6bff871f035444ce83a670df"
    try:
        ab = AdvertiserBearer(
            adv_message=bytearray(pb_advertiser_bearer._contents),
            proxied_device=proxied_device,
        ).verify()
    except ValueError as e:
        print(e)
