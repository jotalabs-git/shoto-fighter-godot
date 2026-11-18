class_name HUD
extends CanvasLayer

## Capa de presentación únicamente: el estado de combate sigue en MatchManager.
## Barras desde los extremos hacia el centro para seguir el esquema arcade.

const BAR_W := 162.0
const P2_BAR_LEFT := 211.0
const P1_COLOR := Color(0.26, 0.82, 0.94)
const P2_COLOR := Color(0.97, 0.31, 0.44)
const DANGER_COLOR := Color(1.0, 0.77, 0.28)
const CRITICAL_COLOR := Color(1.0, 0.31, 0.36)

@onready var p1_name: Label = $P1Name
@onready var p2_name: Label = $P2Name
@onready var p1_fill: ColorRect = $P1Fill
@onready var p2_fill: ColorRect = $P2Fill
@onready var timer_label: Label = $Timer
@onready var msg_label: Label = $Message
@onready var msg_shadow: Label = $MessageShadow
@onready var p1_pips: Label = $P1Pips
@onready var p2_pips: Label = $P2Pips

var p1: Fighter
var p2: Fighter

func set_timer(seconds: int) -> void:
	if timer_label == null:
		return
	timer_label.text = str(seconds)
	timer_label.add_theme_color_override(
		"font_color", CRITICAL_COLOR if seconds <= 10 else Color(1.0, 0.88, 0.65)
	)

func set_rounds(a: int, b: int) -> void:
	if p1_pips != null:
		p1_pips.text = "●".repeat(a)
	if p2_pips != null:
		p2_pips.text = "●".repeat(b)

func set_message(message: String) -> void:
	if msg_label != null:
		msg_label.text = message
	if msg_shadow != null:
		msg_shadow.text = message

func setup(a: Fighter, b: Fighter) -> void:
	p1 = a
	p2 = b
	p1_name.text = CharacterRegistry.display_name(a.character_id)
	p2_name.text = CharacterRegistry.display_name(b.character_id)

func _process(_delta: float) -> void:
	if p1 != null:
		var health_ratio := _ratio(p1)
		p1_fill.size.x = BAR_W * health_ratio
		p1_fill.color = _health_color(health_ratio, P1_COLOR)
	if p2 != null:
		var health_ratio := _ratio(p2)
		var width := BAR_W * health_ratio
		p2_fill.size.x = width
		p2_fill.position.x = P2_BAR_LEFT + (BAR_W - width)
		p2_fill.color = _health_color(health_ratio, P2_COLOR)

func _ratio(fighter: Fighter) -> float:
	return clampf(float(fighter.health) / maxf(float(fighter.max_health), 1.0), 0.0, 1.0)

func _health_color(ratio: float, normal_color: Color) -> Color:
	if ratio <= 0.20:
		return CRITICAL_COLOR
	if ratio <= 0.40:
		return DANGER_COLOR
	return normal_color
