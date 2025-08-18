"""Utility functions for generating UUIDs.

This module provides:
- uuid7: Generates a UUID version 7 using current timestamp and random bytes.
"""

import os
import time
import uuid


def uuid7():
    """Generate a UUID version 7 using the current timestamp and random bytes.

    Returns:
    -------
    uuid.UUID
        A UUIDv7 object generated from the current timestamp and random bytes.
    """
    # random bytes
    value = bytearray(os.urandom(16))

    # current timestamp in ms
    timestamp = int(time.time() * 1000)

    # timestamp
    value[0] = (timestamp >> 40) & 0xFF
    value[1] = (timestamp >> 32) & 0xFF
    value[2] = (timestamp >> 24) & 0xFF
    value[3] = (timestamp >> 16) & 0xFF
    value[4] = (timestamp >> 8) & 0xFF
    value[5] = timestamp & 0xFF

    # version and variant
    value[6] = (value[6] & 0x0F) | 0x70
    value[8] = (value[8] & 0x3F) | 0x80

    return uuid.UUID(bytes=bytes(value))
