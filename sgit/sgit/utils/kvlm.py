from typing import Optional, Dict, Union, List


def kvlm_parse(raw: bytes, start: int = 0, dct: Optional[Dict[Optional[bytes], Union[bytes, List[bytes]]]] = None
               ) -> Dict[Optional[bytes], Union[bytes, List[bytes]]]:
    """
    Parse a key-value list with message (KVLm) from raw commit/tag/obj data.

    Args:
        raw: Raw bytes of commit/tag object.
        start: Start index in raw bytes.
        dct: Dictionary to store parsed key-value pairs.

    Returns:
        Dictionary mapping keys (bytes or None) to values (bytes or list of bytes).
        The commit message is stored under key `None`.
    """
    if dct is None:
        dct = {}

    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    # If no key-value pair remains, the rest is the commit message
    if (spc < 0) or (nl < spc):
        assert nl == start
        dct[None] = raw[start + 1:]  # Message starts after the newline
        return dct

    key = raw[start:spc]

    # Find the end of the value (handles multi-line values with space continuation)
    end = start
    while True:
        end = raw.find(b'\n', end + 1)
        if end == -1 or end + 1 >= len(raw):
            break
        if raw[end + 1] != ord(' '):
            break

    # Replace continuation space sequences with single newline
    value = raw[spc + 1:end].replace(b'\n ', b'\n')

    # Handle multiple values for the same key
    if key in dct:
        if isinstance(dct[key], list):
            dct[key].append(value)
        else:
            dct[key] = [dct[key], value]
    else:
        dct[key] = value

    # Recurse to parse remaining raw bytes
    return kvlm_parse(raw, start=end + 1, dct=dct)


def kvlm_serialize(kvlm: Dict[Optional[bytes], Union[bytes, List[bytes]]]) -> bytes:
    """
    Serialize a KVLm dictionary back to raw bytes.

    Args:
        kvlm: Dictionary of key-values and message (key `None`).

    Returns:
        Serialized bytes representing commit/tag/tree object.
    """
    res = b''

    for k in kvlm.keys():
        if k is None:
            continue
        val = kvlm[k]
        if not isinstance(val, list):
            val = [val]

        for v in val:
            # Replace newlines with space continuation for multi-line values
            res += k + b' ' + v.replace(b'\n', b'\n ') + b'\n'

    # Append the commit/tag message at the end
    res += b'\n' + kvlm[None]
    return res
