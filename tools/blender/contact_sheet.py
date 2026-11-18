"""Build a PNG sheet at native resolution and an index of pose coordinates."""
import argparse
import math
from pathlib import Path

from common import read_json, write_json
from png import read_png, write_png


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("poses", nargs="*", help="Acción o acción:índice. Por defecto, pose central de cada acción.")
    parser.add_argument("--columns", type=int, default=5)
    args = parser.parse_args()
    if args.columns < 1:
        parser.error("--columns debe ser positivo")
    manifest = read_json(args.folder / "manifest.json")
    density = manifest.get("pixels_per_unit", 1)
    cell_w, cell_h = (side * density for side in manifest["canvas"])
    gutter = 4
    poses = args.poses or list(manifest["anims"])
    columns = min(args.columns, len(poses))
    width = columns * (cell_w + gutter) + gutter
    height = math.ceil(len(poses) / columns) * (cell_h + gutter) + gutter
    background = (38, 34, 54)
    canvas = bytearray(bytes((*background, 255)) * (width * height))
    index = []
    for i, pose in enumerate(poses):
        action, sep, frame = pose.partition(":")
        count = manifest["anims"][action]["frames"]
        frame = int(frame) if sep else count // 2
        if not 0 <= frame < count:
            parser.error(f"{pose}: índice fuera de rango")
        path = args.folder / action / f"{frame:03d}.png"
        _, _, pixels = read_png(path, (cell_w, cell_h))
        x = gutter + i % columns * (cell_w + gutter)
        y = gutter + i // columns * (cell_h + gutter)
        index.append({"action": action, "frame": frame, "xy": [x, y]})
        ground = manifest["axis"][1] * density
        for row in range(cell_h):
            bg = (60, 52, 76) if row == ground else background
            for col in range(cell_w):
                offset = (row * cell_w + col) * 4
                alpha = pixels[offset + 3]
                target = ((y + row) * width + x + col) * 4
                for rgb in range(3):
                    canvas[target + rgb] = (pixels[offset + rgb] * alpha + bg[rgb] * (255 - alpha)) // 255
    write_png(args.output, width, height, canvas)
    write_json(args.output.with_suffix(".json"), index)
    print(f"{args.output}: {len(index)} poses")


if __name__ == "__main__":
    main()
