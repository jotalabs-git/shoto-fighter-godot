"""Small RGBA8 PNG reader/writer for the Blender export contract."""
import struct
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def paeth(left, above, diagonal):
    estimate = left + above - diagonal
    a, b, c = (abs(estimate - value) for value in (left, above, diagonal))
    return left if a <= b and a <= c else above if b <= c else diagonal


def chunks(data):
    if not data.startswith(SIGNATURE):
        raise ValueError("firma PNG inválida")
    pos = len(SIGNATURE)
    while pos + 12 <= len(data):
        size, kind = struct.unpack_from(">I4s", data, pos)
        end = pos + 8 + size
        if end + 4 > len(data):
            raise ValueError("chunk truncado")
        part = data[pos + 8:end]
        if zlib.crc32(kind + part) != struct.unpack_from(">I", data, end)[0]:
            raise ValueError(f"CRC inválido en {kind!r}")
        yield kind, part, data[pos:end + 4]
        if kind == b"IEND":
            if size or end + 4 != len(data):
                raise ValueError("IEND inválido")
            return
        pos = end + 4
    raise ValueError("falta IEND")


def strip_text_metadata(path):
    # Blender includes host paths and wall-clock render times in textual chunks.
    data = path.read_bytes()
    cleaned = SIGNATURE + b"".join(raw for kind, _, raw in chunks(data)
                                   if kind not in {b"tEXt", b"zTXt", b"iTXt"})
    if cleaned != data:
        path.write_bytes(cleaned)


def read_png(path, expected_size=None, *, alpha_only=False):
    compressed = bytearray()
    width = height = 0
    for index, (kind, part, _) in enumerate(chunks(path.read_bytes())):
        if kind == b"IHDR":
            if index != 0 or len(part) != 13:
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
    if not width or not compressed:
        raise ValueError("falta IHDR o IDAT")
    stride = width * 4
    limit = (stride + 1) * height
    decoder = zlib.decompressobj()
    scanlines = decoder.decompress(compressed, limit + 1)
    if len(scanlines) != limit or not decoder.eof or decoder.unused_data:
        raise ValueError("longitud de píxeles inválida")
    decoded = bytearray()
    pixel_size = 1 if alpha_only else 4
    above = bytes(width * pixel_size)
    for start in range(0, len(scanlines), stride + 1):
        filter_id = scanlines[start]
        row = scanlines[start + 1:start + 1 + stride]
        current = bytearray(row[3::4] if alpha_only else row)
        if filter_id == 1:
            for col in range(pixel_size, len(current)):
                current[col] = (current[col] + current[col - pixel_size]) & 255
        elif filter_id == 2:
            current = bytearray((value + up) & 255 for value, up in zip(current, above))
        elif filter_id == 3:
            for col, up in enumerate(above):
                left = current[col - pixel_size] if col >= pixel_size else 0
                current[col] = (current[col] + (left + up) // 2) & 255
        elif filter_id == 4:
            for col, up in enumerate(above):
                left = current[col - pixel_size] if col >= pixel_size else 0
                diagonal = above[col - pixel_size] if col >= pixel_size else 0
                current[col] = (current[col] + paeth(left, up, diagonal)) & 255
        elif filter_id != 0:
            raise ValueError("filtro PNG desconocido")
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
