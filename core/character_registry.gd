class_name CharacterRegistry
extends RefCounted

## Catálogo de identidades visuales, separado de Characters (estadísticas
## y especiales). Los músicos reutilizan la jugabilidad actual.
const ENTRIES := {
	"kaze": {"name": "KAZE", "folder": "", "tint": Color(0.72, 0.82, 1.0)},
	"homura": {"name": "HOMURA", "folder": "", "tint": Color(1.0, 0.86, 0.82)},
	"guitarist": {"name": "EL GUITARRISTA", "folder": "res://assets/characters/guitarist", "tint": Color(0.72, 0.82, 1.0), "art_facing": 1},
	"frontman": {"name": "EL FRONTMAN", "folder": "res://assets/characters/frontman", "tint": Color(1.0, 0.86, 0.82), "art_facing": -1},
	"bruce": {"name": "BRUCE DICKINSON", "folder": "", "tint": Color(0.85, 0.75, 0.66)},
}

static func display_name(character_id: String) -> String:
	if ENTRIES.has(character_id):
		return str(ENTRIES[character_id]["name"])
	return character_id.to_upper()

static func asset_folder(character_id: String) -> String:
	if ENTRIES.has(character_id):
		return str(ENTRIES[character_id]["folder"])
	return ""

static func tint(character_id: String) -> Color:
	if ENTRIES.has(character_id):
		return ENTRIES[character_id]["tint"]
	return Color.WHITE

## Orientación del arte original; no cambia la dirección física del Fighter.
## Blender exportó al cantante mirando hacia la izquierda y al guitarrista
## hacia la derecha. Se compensa solo al dibujar el sprite.
static func art_facing(character_id: String) -> int:
	if ENTRIES.has(character_id):
		return int(ENTRIES[character_id].get("art_facing", 1))
	return 1
