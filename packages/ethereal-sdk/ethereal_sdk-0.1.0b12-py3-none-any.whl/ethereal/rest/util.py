import time
import uuid


def uuid_to_bytes32(uuid_str: str) -> str:
    """Converts UUID string to bytes32 hex format.

    Args:
        uuid_str (str): UUID string to convert.

    Returns:
        str: Bytes32 hex string prefixed with '0x'.
    """
    uuid_obj = uuid.UUID(uuid_str)

    # remove hyphens and convert to hex
    uuid_hex = uuid_obj.hex

    # pad the hex to make it 32 bytes
    padded_hex = uuid_hex.rjust(64, "0")

    return "0x" + padded_hex


def generate_nonce() -> str:
    """Generates a timestamp-based nonce.

    Returns:
        str: Current timestamp in nanoseconds as string.
    """
    return str(time.time_ns())
