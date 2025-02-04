from classes.network_pdu import NetworkPdu
from src.proxied_device import ProxiedDevice


class NetworkLayerBearer:
    def __init__(self, networkPDU: NetworkPdu, proxied_device: ProxiedDevice):
        self._network_pdu = networkPDU
        self._proxied_device = proxied_device

    def set_iv_index_nid(self):
        return self._network_pdu.ivi_nid

    def decrement_ttl(self):
        # convert ttl to int and decrement by one
        if self._network_pdu._ttl == b"\x00":
            raise ValueError("TTL is already 0")
        else:
            ttl = int.from_bytes(self._network_pdu._ttl, "big") - 1
            self._network_pdu._ttl = ttl.to_bytes(1, "big")
        return self

    def increment_seq(self):
        # convert seq to int and increment by one
        seq = int.from_bytes(self._network_pdu._seq, "big") + 1
        self._network_pdu._seq = seq.to_bytes(3, "big")
        return self

    def set_src(self):
        self._network_pdu._src = self._proxied_device._unicast_address
        return self

    def set_dst(self):
        self._network_pdu._dst = self._network_pdu._dst
        return self

    def set_net_mic(self):
        # self._network_pdu._net_mic = self._network_pdu.encrypt_data(
        #     dst=self._network_pdu._dst,
        #     transport_pdu=self._network_pdu._transport_pdu,
        #     key=self._proxied_device._network_encryption_key,
        #     nonce=self._proxied_device._nonce,
        # )._netMic

        # TODO: not implemented on raspi pico since cannot use encrypt data via ccm
        self._network_pdu._net_mic = bytearray.fromhex("a6a127953989b810")
        return self

    def create_adv_message(self):
        self.set_iv_index_nid()
        self.decrement_ttl()
        self.increment_seq()
        self.set_src()
        self.set_dst()
        self.set_net_mic()
        print("created adv message")
        return self._network_pdu._network_pdu


if __name__ == "__main__":
    proxiedDevice = ProxiedDevice(
        unicast_address=bytearray.fromhex("12345678"),
        nid=bytearray.fromhex("68"),
        network_encryption_key=bytearray.fromhex("0953fa93e7caac9638f58820220a398e"),
        privacy_keys=bytearray.fromhex("8b84eedec100067d670971dd2aa700cf"),
        iv_index=bytearray.fromhex("12345678"),
        nonce=bytearray.fromhex("008b0148352345000012345678"),
    )
    networkPdu = (
        NetworkPdu(
            network_pdu_message=bytearray.fromhex(
                "68e476b5579c980d0d730f94d7f3509df987bb417eb7c05f"
            )
        )
        .deconstruct_pdu()
        .de_obfusicate_data(
            IVIndex=bytearray.fromhex("12345678"),
            key=bytearray.fromhex("8b84eedec100067d670971dd2aa700cf"),
        )
    )

    networkBearer = NetworkLayerBearer(
        networkPDU=networkPdu, proxied_device=proxiedDevice
    ).create_adv_message()
