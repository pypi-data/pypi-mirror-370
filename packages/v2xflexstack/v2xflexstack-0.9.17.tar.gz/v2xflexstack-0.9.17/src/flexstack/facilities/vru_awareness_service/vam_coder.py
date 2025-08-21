import asn1tools

from .vam_asn1 import VAM_ASN1_DESCRIPTIONS


class VAMCoder:
    """
    Class for encoding/decoding Vulnerable Road User Awareness Message (VAM)

    Attributes
    ----------
    asn_coder : asn1tools.Coder
        ASN.1 coder.
    """

    def __init__(self) -> None:
        """
        Initialize the VAM Coder.
        """
        self.asn_coder = asn1tools.compile_string(
            VAM_ASN1_DESCRIPTIONS, codec='uper')

    def encode(self, vam: dict) -> bytes:
        """
        Encodes a VAM message.

        Parameters
        ----------
        vam : dict
            VAM message.

        Returns
        -------
        bytes
            Encoded VAM message.
        """
        return self.asn_coder.encode('VAM', vam)

    def decode(self, vam: bytes) -> dict:
        """
        Decodes a VAM message.

        Parameters
        ----------
        vam : bytes
            Encoded VAM message.

        Returns
        -------
        dict
            VAM message.
        """
        return self.asn_coder.decode('VAM', vam)
