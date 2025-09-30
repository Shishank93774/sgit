def kvlm_parse(raw, start=0, dct=None):
    if dct is None:
        dct = {}

    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    if (spc < 0) or (nl < spc):
        assert nl == start
        dct[None] = raw[start + 1:]
        return dct

    key = raw[start:spc]

    end = start
    while True:
        end = raw.find(b'\n', end + 1)
        if end == -1 or end + 1 >= len(raw):
            break
        if raw[end + 1] != ord(' '):
            break

    value = raw[spc + 1:end].replace(b'\n ', b'\n')

    if key in dct:
        if isinstance(dct[key], list):
            dct[key].append(value)
        else:
            dct[key] = [dct[key], value]
    else:
        dct[key] = value

    return kvlm_parse(raw, start=end + 1, dct=dct)

def kvlm_serialize(kvlm):
    res = b''

    for k in kvlm.keys():
        if k is None:
            continue
        val = kvlm[k]
        if not isinstance(val, list):
            val = [val]

        for v in val:
            res += k + b' ' + v.replace(b'\n', b'\n ') + b'\n'

    res += b'\n' + kvlm[None]
    return res