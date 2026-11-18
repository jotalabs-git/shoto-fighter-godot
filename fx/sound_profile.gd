class_name SoundProfile
extends RefCounted

## Claves estables para el banco de sonido. Separadas de la reproducción.
static func impact_key(move: MoveData, blocked: bool = false) -> String:
	if blocked:
		return "block"
	if move == null:
		return "hit_punch_medium"
	if move.spawns_projectile:
		return "hit_energy"
	if move.causes_knockdown:
		return "hit_sweep"
	var name := move.move_name.to_lower()
	var kind := "kick" if ".lk" in name or ".mk" in name or ".hk" in name or name == "tatsu" else "punch"
	var weight := "light"
	if move.damage >= 85:
		weight = "heavy"
	elif move.damage >= 50:
		weight = "medium"
	return "hit_%s_%s" % [kind, weight]

static func attack_weight(move: MoveData) -> String:
	if move == null:
		return "light"
	return "heavy" if move.damage >= 80 or move.is_special else "light"

static func fighter_voice(character_id: String) -> String:
	# Los personajes originales y el fallback tienen un banco neutro.
	if character_id == "guitarist" or character_id == "frontman":
		return character_id
	return "neutral"
