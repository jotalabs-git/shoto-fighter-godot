extends Control

## Visual de arcade rock para el menu, sin modificar los modos ni sus acciones.
func _ready() -> void:
	_apply_brand()
	$BtnCredits.pressed.connect(func() -> void: get_tree().change_scene_to_file("res://ui/credits.tscn"))
	$BtnVoices.pressed.connect(_toggle_voice_style)
	_update_voice_button()
	$VBox/Btn2P.pressed.connect(_start.bind(false, "medium"))
	$VBox/BtnEasy.pressed.connect(_start.bind(true, "easy"))
	$VBox/BtnMedium.pressed.connect(_start.bind(true, "medium"))
	$VBox/BtnHard.pressed.connect(_start.bind(true, "hard"))

func _apply_brand() -> void:
	var display_font := RockBrand.font_file("display")
	if display_font != null:
		$TitleRock.add_theme_font_override("font", display_font)
		$TitleKombat.add_theme_font_override("font", display_font)
	var ui_font := RockBrand.font_file("ui")
	if ui_font != null:
		$Subtitle.add_theme_font_override("font", ui_font)
		$Hint.add_theme_font_override("font", ui_font)
	for button in [$VBox/Btn2P, $VBox/BtnEasy, $VBox/BtnMedium, $VBox/BtnHard, $BtnCredits, $BtnVoices]:
		if ui_font != null:
			button.add_theme_font_override("font", ui_font)
		button.add_theme_stylebox_override("normal", RockBrand.button_style())
		button.add_theme_stylebox_override("hover", RockBrand.button_style(true))
		button.add_theme_stylebox_override("pressed", RockBrand.button_style(true))
		button.add_theme_stylebox_override("focus", RockBrand.button_style(true))
		button.add_theme_color_override("font_color", RockBrand.METAL_SILVER)
		button.add_theme_color_override("font_hover_color", RockBrand.AMP_YELLOW)
		button.add_theme_color_override("font_pressed_color", RockBrand.NEON_BLUE)
		button.add_theme_font_size_override("font_size", 8 if button == $BtnCredits or button == $BtnVoices else 11)
		button.custom_minimum_size.y = 0.0 if button == $BtnCredits or button == $BtnVoices else 25.0

func _start(cpu: bool, difficulty: String) -> void:
	GameConfig.set_mode(cpu, difficulty)
	get_tree().change_scene_to_file("res://ui/character_select.tscn")

func _toggle_voice_style() -> void:
	GameConfig.voice_style = "humor" if GameConfig.voice_style == "rock" else "rock"
	_update_voice_button()

func _update_voice_button() -> void:
	$BtnVoices.text = "VOCES: HUMOR" if GameConfig.voice_style == "humor" else "VOCES: ROCK"
