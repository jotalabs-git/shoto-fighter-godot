extends Node

## Config global entre escenas (autoload). El menú la escribe; el MatchManager la lee.

var p2_is_cpu: bool = false
var cpu_difficulty: String = "medium"
var show_boxes: bool = false   # activar cajas de depuración con F1
var voice_style: String = "rock"  # rock / humor (requiere voces CC BY instaladas)

func set_mode(cpu: bool, difficulty: String) -> void:
	p2_is_cpu = cpu
	cpu_difficulty = difficulty
