extends Control

## Créditos visibles desde el menú. Incluye atribuciones obligatorias CC BY.
func _ready() -> void:
	var bg := ColorRect.new()
	bg.color = RockBrand.STAGE_BLACK
	add_child(bg)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

	var title := Label.new()
	title.text = "CREDITOS / AUDIO"
	title.position = Vector2(20, 10)
	title.size = Vector2(344, 21)
	title.add_theme_color_override("font_color", RockBrand.AMP_YELLOW)
	title.add_theme_font_size_override("font_size", 16)
	add_child(title)

	var scroll := ScrollContainer.new()
	scroll.position = Vector2(19, 37)
	scroll.size = Vector2(346, 139)
	add_child(scroll)
	var text_view := RichTextLabel.new()
	text_view.bbcode_enabled = true
	text_view.fit_content = true
	text_view.scroll_active = false
	text_view.custom_minimum_size = Vector2(329, 0)
	text_view.add_theme_font_size_override("normal_font_size", 10)
	text_view.add_theme_color_override("default_color", RockBrand.METAL_SILVER)
	text_view.text = """[color=#00E5FF]IMPACTOS Y LOCUCIONES ARCADE[/color]
Kenney - Impact Sounds y Voiceover Pack: Fighter.
Licencia: Creative Commons CC0 1.0.
[url=https://kenney.nl]kenney.nl[/url]

[color=#CC00FF]VOCES HUMORISTICAS / ATRIBUCION[/color]
24 cute fighting game voice recordings
Autor: bart (OpenGameArt). Licencia: CC BY 3.0.
[url=https://opengameart.org/content/24-cute-fighting-game-voice-recordings]Fuente: OpenGameArt.org[/url]
[url=https://creativecommons.org/licenses/by/3.0/]Licencia CC BY 3.0[/url]
Se seleccionan y renombran tomas al instalar.

[color=#00E5FF]GOLPES ADICIONALES[/color]
37 hits/punches - Independent.nu; CC0 1.0.
[url=https://opengameart.org/content/37-hitspunches]Fuente: OpenGameArt.org[/url]

[color=#FFC400]SONNISS (OPCIONAL)[/color]
GameAudioGDC: licencia especifica, no CC0.
Requiere descarga propia del paquete original.
[url=https://sonniss.com/gdc-bundle-license/]Terminos de Sonniss[/url]

Audio sintetico adicional: creado para Rock Kombat.
"""
	text_view.meta_clicked.connect(_open_url)
	scroll.add_child(text_view)

	var back := Button.new()
	back.text = "VOLVER"
	back.position = Vector2(132, 183)
	back.size = Vector2(120, 27)
	back.add_theme_stylebox_override("normal", RockBrand.button_style())
	back.add_theme_stylebox_override("hover", RockBrand.button_style(true))
	back.add_theme_color_override("font_color", RockBrand.METAL_SILVER)
	back.add_theme_font_size_override("font_size", 10)
	back.pressed.connect(func() -> void: get_tree().change_scene_to_file("res://ui/main_menu.tscn"))
	add_child(back)

func _open_url(url: Variant) -> void:
	OS.shell_open(str(url))
