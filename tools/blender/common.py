"""Paths and JSON shared by Blender and standalone tools."""
import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[1]
ASSETS = ROOT / "assets" / "characters"
SOURCES = TOOLS / "sources"
REFERENCE = ROOT / "assets" / "kfm" / "manifest.json"
SPEC = TOOLS / "character_spec.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def blender_args(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("character", choices=read_json(SPEC)["characters"])
    return parser, sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
