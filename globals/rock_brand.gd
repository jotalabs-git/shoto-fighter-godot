class_name RockBrand
extends RefCounted

## Identidad visual centralizada. Colores de la guia Rock Kombat.
const ROCK_RED := Color("#FF003C")
const STAGE_MAGENTA := Color("#CC00FF")
const NEON_BLUE := Color("#00E5FF")
const AMP_YELLOW := Color("#FFC400")
const METAL_SILVER := Color("#C7C9D1")
const STAGE_BLACK := Color("#0B0B12")

const HUD_BG := Color("#10121D")
const BAR_BG := Color("#1A1D28")
const DEEP_PURPLE := Color("#231230")
const FLOOR := Color("#292536")

static func button_style(focused: bool = false) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = DEEP_PURPLE if focused else HUD_BG
	style.border_color = STAGE_MAGENTA if focused else Color("#56314E")
	style.set_border_width_all(1)
	style.corner_radius_top_left = 1
	style.corner_radius_bottom_right = 1
	style.content_margin_left = 11.0
	style.content_margin_right = 11.0
	style.content_margin_top = 3.0
	style.content_margin_bottom = 3.0
	return style

## El fallback nativo permite abrir el proyecto si faltan los TTF incluidos.
static var _font_cache: Dictionary = {}

static func font_file(role: String) -> Font:
	var filename := ""
	match role:
		"display":
			filename = "MetalMania-Regular.ttf"
		"impact":
			filename = "Bangers-Regular.ttf"
		"ui":
			filename = "Oxanium-Variable.ttf"
		_:
			return null
	var path := "res://assets/fonts/" + filename
	if _font_cache.has(path):
		return _font_cache[path]
	if not ResourceLoader.exists(path):
		return null
	var loaded := load(path) as Font
	if loaded != null:
		_font_cache[path] = loaded
	return loaded
