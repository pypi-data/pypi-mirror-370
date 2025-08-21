import asn1tools
from .asn1.denm_asn1 import DENM_ASN1_DESCRIPTIONS


class DENMCoder:
    """
    Class for encoding/decoding Decentralized Environment Notification Messages (DENM)

    Attributes
    ----------
    asn_coder : asn1tools.Coder
        ASN.1 coder.
    """

    def __init__(self) -> None:
        """
        Initialize the DENM Coder.
        """
        self.asn_coder = asn1tools.compile_string(
            DENM_ASN1_DESCRIPTIONS, codec='uper')

    def encode(self, denm: dict) -> bytes:
        """
        Encodes a DENM message.

        Parameters
        ----------
        denm : dict
            DENM message.

        Returns
        -------
        bytes
            Encoded DENM message.
        """
        return self.asn_coder.encode('DENM', denm)

    def decode(self, denm: bytes) -> dict:
        """
        Decodes a DENM message.

        Parameters
        ----------
        denm : bytes
            Encoded DENM message.

        Returns
        -------
        dict
            DENM message.
        """
        return self.asn_coder.decode('DENM', denm)
