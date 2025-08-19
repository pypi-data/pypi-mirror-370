"""JIS X 0201 Codec required for JIS8 encoding of JIS8."""
import codecs

jis8_decoding_map = codecs.make_identity_dict(range(256))  # type: ignore[attr-defined]
jis8_decoding_map.update({
    0x005C: 0x00A5,  # Yen Sign
    0x007E: 0x203E,  # Overline
})

for i in range(0x00A1, 0x00E0):
    jis8_decoding_map[i] = i + 0xFEC0

jis8_encoding_map = codecs.make_encoding_map(jis8_decoding_map)  # type: ignore[attr-defined]


def _jis_x_0201_encode(data, errors="strict"):
    return codecs.charmap_encode(data, errors, jis8_encoding_map)


def _jis_x_0201_decode(data, errors="strict"):
    return codecs.charmap_decode(data, errors, jis8_decoding_map)


def _jis_x_0201_search(name):
    if name == "jis_8":
        return codecs.CodecInfo(encode=_jis_x_0201_encode, decode=_jis_x_0201_decode, name="jis_8")

    return None


# register the codec
codecs.register(_jis_x_0201_search)
