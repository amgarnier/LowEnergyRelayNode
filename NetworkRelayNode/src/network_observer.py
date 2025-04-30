from src.advertiser_bearer import AdvertiserBearer
from src.proxied_device import ProxiedDevice
from classes.network_pdu import NetworkPdu


class MessageCache:
    def __init__(self):
        self._cache = [AdvertiserBearer()]  # cache of 15 Advertiser Bearers
        self._cache_size = 15  # max size of cache is 15

    def verify(self, advertiser_bearer: AdvertiserBearer):
        # check if the message is in the cache
        for i in self._cache:
            if i._adv_message == advertiser_bearer._adv_message:
                raise ValueError("message is in cache")
                print(f"message is in cache")
                return True
        return False

    def append(self, advertiser_bearer: AdvertiserBearer):
        # append the message to the cache
        self._cache.append(advertiser_bearer)
        # check if the cache is full
        if len(self._cache) > self._cache_size:
            self._cache.pop(0)
        return self


class NetworkObserver:
    def __init__(
        self, proxied_device: ProxiedDevice, advertiser_bearer: AdvertiserBearer
    ):
        self._proxied_device = proxied_device
        self._advertiser_bearer = advertiser_bearer
        self._network_pdu = NetworkPdu(
            network_pdu_message=advertiser_bearer._adv_message[3:],
        )
        self._network_pdu = self._network_pdu.deconstruct_pdu()

    def verify_nid(self):

        # TODO: update to only be the last 7
        nid = self._network_pdu.ivi_nid
        if nid != self._proxied_device._nid:
            raise ValueError("Invalid NID")
        return self

    def verify_mic_decrypt(self):
        try:
            self._network_pdu._encrypted_data_message = self._network_pdu.decrypt_data(
                key=self._proxied_device._network_encryption_key,
                nonce=self._proxied_device._nonce,
                mic=self._network_pdu.net_mic,
            )
        except Exception as e:
            print(e)
        return self

    def verify_network_cache(self):
        return self

    def de_obfuscate(self):
        self._network_pdu._obfuscated_data = self._network_pdu.de_obfusicate_data(
            IVIndex=self._proxied_device._iv_index,
            key=self._proxied_device._privacy_key,
        )._obfuscated_data
        return self

    def verify_local(self):
        # check
        if self._network_pdu._dst == self._proxied_device._unicast_address:
            raise ValueError("This is a local package do not re-transmit")
        return self

    def network_caches(self, message_cache: MessageCache):
        if not message_cache.verify(advertiser_bearer=self._advertiser_bearer):
            message_cache.append(advertiser_bearer=self._advertiser_bearer)

    def observe(self, message_cache: MessageCache):
        # this was removed so that the message is just returned
        # self.verify_nid() // verify nid
        self.verify_mic_decrypt()  # mock decryption of data
        # self.network_caches(message_cache=message_cache)
        # self.de_obfuscate()
        # self.verify_local()
        return self._network_pdu

    def return_network_pdu(self):
        return self._network_pdu


if __name__ == "__main__":
    # creaete proxied device and then the advertiser beaer for testing
    proxiedDevice: ProxiedDevice = ProxiedDevice(
        unicast_address=bytearray.fromhex("1201"),
        network_key=bytearray.fromhex("7dd7364cd842ad18c17c2b820c84c3d6"),
        nonce=bytearray.fromhex("00800000011201000012345678"),
        iv_index=bytearray.fromhex("12345678"),
    ).create_network_keys()

    advertiserBearer = AdvertiserBearer(
        proxied_device=proxiedDevice,
        adv_message=bytearray.fromhex(
            "1e202a68eca487516765b5e5bfdacbaf6cb7fb6bff871f035444ce83a670df"
        ),
    )

    messageCache = MessageCache()

    # now create the observer
    networkPdu: NetworkPdu = NetworkObserver(
        proxied_device=proxiedDevice,
        advertiser_bearer=advertiserBearer,
    ).observe(message_cache=messageCache)

    print(f"Dst: {networkPdu._dst.hex()}")
