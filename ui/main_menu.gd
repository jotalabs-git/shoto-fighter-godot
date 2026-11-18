extends Control

## Visual de arcade rock para el menu, sin modificar los modos ni sus acciones.
func _ready() -> void:
	_apply_brand()
	$VBox/Btn2P.pressed.connect(_start.bind(false, "medium"))
	$VBox/BtnEasy.pressed.connect(_start.bind(true, "easy"))
	$VBox/BtnMedium.pressed.connect(_start.bind(true, "medium"))
	$VBox/BtnHard.pressed.connect(_start.bind(true, "hard"))

func _apply_brand() -> void:
	for button in [$VBox/Btn2P, $VBox/BtnEasy, $VBox/BtnMedium, $VBox/BtnHard]:
		button.add_theme_stylebox_override("normal", RockBrand.button_style())
		button.add_theme_stylebox_override("hover", RockBrand.button_style(true))
		button.add_theme_stylebox_override("pressed", RockBrand.button_style(true))
		button.add_theme_stylebox_override("focus", RockBrand.button_style(true))
		button.add_theme_color_override("font_color", RockBrand.METAL_SILVER)
		button.add_theme_color_override("font_hover_color", RockBrand.AMP_YELLOW)
		button.add_theme_color_override("font_pressed_color", RockBrand.NEON_BLUE)
		button.add_theme_font_size_override("font_size", 11)
		button.custom_minimum_size.y = 25.0

func _start(cpu: bool, difficulty: String) -> void:
	GameConfig.set_mode(cpu, difficulty)
	get_tree().change_scene_to_file("res://match/match.tscn")
