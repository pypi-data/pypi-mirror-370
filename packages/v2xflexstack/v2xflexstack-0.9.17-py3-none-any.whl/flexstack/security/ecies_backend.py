class ECIESBackend:
    """
    Interface for ECIES backends.
    """

    def create_key(self) -> int:
        """
        Creates a new key pair. Returns the identifier of the key.
        """
        raise NotImplementedError("All the ECIES backends should implement this")

    def get_public_key(self, identifier: int) -> dict:
        """
        Returns the public key of the key pair with the id.
        It returns as a dict to be oer encoded as PublicEncryptionKey.
        """
        raise NotImplementedError("All the ECIES backends should implement this")

    def encrypt(self, data: bytes, public_key: dict) -> bytes:
        """
        Encrypts the array of bytes. With the public key.
        The public key has to be received as PublicEncryptionKey.
        """
        raise NotImplementedError("All the ECIES backends should implement this")

    def decrypt(self, data: bytes, identifier: int) -> bytes:
        """
        Decrypts the array of bytes. With the private key.
        """
        raise NotImplementedError("All the ECIES backends should implement this")
