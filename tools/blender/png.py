"""Small RGBA8 PNG reader/writer for the Blender export contract."""
import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def paeth(left, above, diagonal):
    estimate = left + above - diagonal
    a, b, c = (abs(estimate - value) for value in (left, above, diagonal))
    return left if a <= b and a <= c else above if b <= c else diagonal


def read_png(path, expected_size=None):
    data = path.read_bytes()
    if not data.startswith(SIGNATURE):
        raise ValueError("firma PNG inválida")
    pos = len(SIGNATURE)
    compressed = bytearray()
    width = height = 0
    while pos + 12 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, pos)
        end = pos + 8 + size
        if end + 4 > len(data):
            raise ValueError("chunk truncado")
        part = data[pos + 8:end]
        if zlib.crc32(kind + part) != struct.unpack_from(">I", data, end)[0]:
            raise ValueError(f"CRC inválido en {kind!r}")
        if kind == b"IHDR":
            if pos != len(SIGNATURE) or size != 13:
                raise ValueError("IHDR inválido")
            width, height, bits, color, method, filters, interlace = struct.unpack(">IIBBBBB", part)
            if (bits, color, method, filters, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("se requiere PNG RGBA8 no entrelazado")
            if not (0 < width <= 4096 and 0 < height <= 4096):
                raise ValueError("dimensiones fuera de rango")
            if expected_size is not None and (width, height) != tuple(expected_size):
                raise ValueError(f"canvas {(width, height)} distinto de {expected_size}")
        elif kind == b"IDAT":
            compressed.extend(part)
        elif kind == b"IEND":
            if size or end + 4 != len(data):
                raise ValueError("IEND inválido")
            break
        pos = end + 4
    else:
        raise ValueError("falta IEND")
    if not width or not compressed:
        raise ValueError("falta IHDR o IDAT")
    stride = width * 4
    limit = (stride + 1) * height
    decoder = zlib.decompressobj()
    scanlines = decoder.decompress(compressed, limit + 1)
    if len(scanlines) != limit or not decoder.eof or decoder.unused_data:
        raise ValueError("longitud de píxeles inválida")
    decoded = bytearray()
    above = bytes(stride)
    for start in range(0, len(scanlines), stride + 1):
        filter_id = scanlines[start]
        current = bytearray(scanlines[start + 1:start + 1 + stride])
        if filter_id > 4:
            raise ValueError("filtro PNG desconocido")
        if filter_id:
            for col in range(stride):
                left = current[col - 4] if col >= 4 else 0
                diagonal = above[col - 4] if col >= 4 else 0
                up = above[col]
                prediction = (left, up, (left + up) // 2, paeth(left, up, diagonal))[filter_id - 1]
                current[col] = (current[col] + prediction) & 255
        decoded.extend(current)
        above = current
    return width, height, decoded


def write_png(path, width, height, pixels):
    def chunk(kind, part):
        return struct.pack(">I", len(part)) + kind + part + struct.pack(">I", zlib.crc32(kind + part))

    stride = width * 4
    raw = b"".join(b"\x00" + pixels[i:i + stride] for i in range(0, len(pixels), stride))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(SIGNATURE + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
