extends Node

## Config global entre escenas (autoload). El menú la escribe; el MatchManager la lee.

var p2_is_cpu: bool = false
var cpu_difficulty: String = "medium"
var show_boxes: bool = false   # activar cajas de depuración con F1
var voice_style: String = "rock"  # rock / humor (requiere voces CC BY instaladas)
var fighter_presentation: StringName = &"3d"
var p1_character_id: String = "guitarist"
var p2_character_id: String = "frontman"
var present_next_match := false

func set_mode(cpu: bool, difficulty: String) -> void:
	p2_is_cpu = cpu
	cpu_difficulty = difficulty

func set_characters(p1_id: String, p2_id: String) -> void:
	if CharacterRegistry.selectable_ids().has(p1_id):
		p1_character_id = p1_id
	if CharacterRegistry.selectable_ids().has(p2_id):
		p2_character_id = p2_id
