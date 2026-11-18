class_name CharacterRegistry
extends RefCounted

## Catálogo de identidades visuales, separado de Characters (estadísticas
## y especiales). Los dos músicos provisionales reutilizan la jugabilidad
## actual hasta diseñar movimientos propios.
const ENTRIES := {
	"kaze": {"name": "KAZE", "folder": "", "tint": Color(0.72, 0.82, 1.0)},
	"homura": {"name": "HOMURA", "folder": "", "tint": Color(1.0, 0.86, 0.82)},
	"guitarist": {"name": "EL GUITARRISTA", "folder": "res://assets/characters/guitarist", "tint": Color(0.72, 0.82, 1.0)},
	"frontman": {"name": "EL FRONTMAN", "folder": "res://assets/characters/frontman", "tint": Color(1.0, 0.86, 0.82)},
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
