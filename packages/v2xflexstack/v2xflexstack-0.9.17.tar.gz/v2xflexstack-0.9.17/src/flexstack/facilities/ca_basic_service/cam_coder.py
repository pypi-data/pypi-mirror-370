"""
CAM Coder.

This file contains the class for the CAM Coder.
"""
import asn1tools
from .cam_asn1 import CAM_ASN1_DESCRIPTIONS


class CAMCoder:
    """
    Class for encoding/decoding Cooperative Awareness Messages (CAM)

    Attributes
    ----------
    asn_coder : asn1tools.Coder
        ASN.1 coder.
    """

    def __init__(self) -> None:
        """
        Initialize the CAM Coder.
        """
        self.asn_coder = asn1tools.compile_string(CAM_ASN1_DESCRIPTIONS, codec="uper")

    def encode(self, cam: dict) -> bytes:
        """
        Encodes a CAM message.

        Parameters
        ----------
        cam : dict
            CAM message.

        Returns
        -------
        bytes
            Encoded CAM message.
        """
        return self.asn_coder.encode("CAM", cam)

    def decode(self, cam: bytes) -> dict:
        """
        Decodes a CAM message.

        Parameters
        ----------
        cam : bytes
            Encoded CAM message.

        Returns
        -------
        dict
            CAM message.
        """
        return self.asn_coder.decode("CAM", cam)
