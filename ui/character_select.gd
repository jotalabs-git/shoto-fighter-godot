extends Control
## Arcade roster: two independent selections with live, standing GLB previews.
## The fighting rules stay in Fighter and MatchManager.

## El roster depende del registro único, no de IDs duplicados en la interfaz.
var _ids: Array[String] = []
const CYAN := Color("#00E5FF")
const PINK := Color("#FF315A")
const GOLD := Color("#FFCE52")
const WHITE := Color("#E5E7F2")
const MUTED := Color("#9195B4")
const BG := Color("#0D0C19")

var _indices: Array[int] = [0, 1]
var _confirmed: Array[bool] = [false, false]
var _is_cpu := false
var _models: Array[Node3D] = []
var _viewport_nodes: Array[SubViewport] = []
var _names: Array[Label] = []
var _status: Array[Label] = []
var _cards: Array[Button] = []
var _hints: Label
var _launching := false

func _ready() -> void:
	_ids = CharacterRegistry.selectable_ids()
	_is_cpu = GameConfig.p2_is_cpu
	_indices[0] = maxi(_ids.find(GameConfig.p1_character_id), 0)
	_indices[1] = maxi(_ids.find(GameConfig.p2_character_id), 0)
	if _is_cpu:
		_random_cpu()
	_construct()
	_refresh_all()

func _construct() -> void:
	# Diseño basado en el lienzo lógico 384x216. Los retratos no invaden el roster.
	var bg := ColorRect.new()
	bg.color = BG
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_panel(Vector2(0, 0), Vector2(384, 2), RockBrand.ROCK_RED)
	_panel(Vector2(0, 39), Vector2(384, 1), RockBrand.STAGE_MAGENTA)
	_panel(Vector2(0, 202), Vector2(384, 1), Color("#51304B"))
	_panel(Vector2(1, 51), Vector2(124, 118), Color("#151828"))
	_panel(Vector2(259, 51), Vector2(124, 118), Color("#151828"))
	_panel(Vector2(130, 51), Vector2(124, 118), Color("#181321"))

	_label("ROCK", Vector2(71, 4), Vector2(121, 27), 23, CYAN, HORIZONTAL_ALIGNMENT_RIGHT, "display")
	_label("KOMBAT", Vector2(195, 4), Vector2(126, 27), 23, RockBrand.ROCK_RED, HORIZONTAL_ALIGNMENT_LEFT, "display")
	_label("ELIGI TU LUCHADOR", Vector2(95, 32), Vector2(194, 11), 9, GOLD, HORIZONTAL_ALIGNMENT_CENTER, "impact")

	_label("P1", Vector2(5, 41), Vector2(120, 12), 12, CYAN, HORIZONTAL_ALIGNMENT_LEFT, "impact")
	_label("CPU" if _is_cpu else "P2", Vector2(259, 41), Vector2(120, 12), 12, PINK, HORIZONTAL_ALIGNMENT_RIGHT, "impact")

	for side in 2:
		var x := 2.0 if side == 0 else 260.0
		_add_preview(side, Vector2(x + 1.0, 52.0))
		var name := _label("", Vector2(x, 170), Vector2(122, 16), 10, CYAN if side == 0 else PINK, HORIZONTAL_ALIGNMENT_CENTER, "impact")
		_names.append(name)
		var status := _label("", Vector2(x, 185), Vector2(122, 12), 7, MUTED, HORIZONTAL_ALIGNMENT_CENTER)
		_status.append(status)

	_label("ROSTER", Vector2(132, 47), Vector2(120, 13), 11, WHITE, HORIZONTAL_ALIGNMENT_CENTER, "impact")
	for index in _ids.size():
		var button := Button.new()
		button.position = Vector2(133.0 + float(index % 2) * 61.0, 68.0 + float(index / 2) * 47.0)
		button.size = Vector2(57, 43)
		button.custom_minimum_size = Vector2.ZERO
		button.clip_text = true
		button.add_theme_font_size_override("font_size", 7)
		var ui_font := RockBrand.font_file("ui")
		if ui_font != null:
			button.add_theme_font_override("font", ui_font)
		button.add_theme_color_override("font_color", WHITE)
		button.add_theme_color_override("font_hover_color", GOLD)
		button.add_theme_stylebox_override("hover", _card_style(GOLD, true))
		button.add_theme_stylebox_override("pressed", _card_style(GOLD, true))
		button.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		button.pressed.connect(_pick_card.bind(index))
		add_child(button)
		_cards.append(button)
	_hints = _label("", Vector2(8, 203), Vector2(368, 12), 7, MUTED, HORIZONTAL_ALIGNMENT_CENTER)

func _card_style(color: Color, selected: bool) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color("#30243C") if selected else Color("#202032")
	style.border_color = color
	style.set_border_width_all(2 if selected else 1)
	style.set_corner_radius_all(3)
	style.content_margin_left = 2.0
	style.content_margin_right = 2.0
	style.content_margin_top = 1.0
	style.content_margin_bottom = 1.0
	return style

func _add_preview(side: int, at: Vector2) -> void:
	var holder := SubViewportContainer.new()
	holder.position = at
	holder.size = Vector2(120, 114)
	holder.stretch = true
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(holder)
	var vp := SubViewport.new()
	vp.name = "ModelPreview%d" % (side + 1)
	vp.size = Vector2i(354, 330)
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	holder.add_child(vp)
	_viewport_nodes.append(vp)
	_models.append(null)

	var environment := WorldEnvironment.new()
	var world := Environment.new()
	world.background_mode = Environment.BG_COLOR
	world.background_color = Color.TRANSPARENT
	world.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.ambient_light_color = Color("#DAE9FF")
	world.ambient_light_energy = 0.65
	environment.environment = world
	vp.add_child(environment)

	var camera := Camera3D.new()
	camera.name = "PreviewCamera"
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 3.7
	camera.near = 0.1
	camera.far = 40.0
	camera.position = Vector3(3.6 if side == 0 else -3.6, 2.3, 5.5)
	vp.add_child(camera)
	camera.look_at(Vector3(0, 1.27, 0), Vector3.UP)
	camera.current = true

	for index in 2:
		var light := DirectionalLight3D.new()
		light.light_color = (Color("#FFF0D9") if index == 0 else Color("#A4CFFF"))
		light.light_energy = 1.25 if index == 0 else 0.65
		if index == 0:
			light.rotation_degrees = Vector3(-38, -35 if side == 0 else 35, 0)
		else:
			light.rotation_degrees = Vector3(-20, 120, 0)
		vp.add_child(light)

	# Base discreta tipo escenario de recital, solo en la vista previa.
	var pedestal := MeshInstance3D.new()
	var cylinder := CylinderMesh.new()
	cylinder.top_radius = 0.89
	cylinder.bottom_radius = 0.96
	cylinder.height = 0.16
	pedestal.mesh = cylinder
	pedestal.position = Vector3(0.0, -0.13, 0.0)
	var pedestal_material := StandardMaterial3D.new()
	pedestal_material.albedo_color = Color("#252238")
	pedestal_material.metallic = 0.24
	pedestal_material.roughness = 0.42
	pedestal.material_override = pedestal_material
	vp.add_child(pedestal)

func _label(value: String, pos: Vector2, dimensions: Vector2, font_size: int, color: Color, horizontal: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT, font_role: String = "ui") -> Label:
	var label := Label.new()
	label.text = value
	label.position = pos
	label.size = dimensions
	label.horizontal_alignment = horizontal
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.clip_text = true
	var font := RockBrand.font_file(font_role)
	if font != null:
		label.add_theme_font_override("font", font)
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)
	return label

func _panel(pos: Vector2, dimensions: Vector2, color: Color) -> void:
	var panel := ColorRect.new()
	panel.position = pos
	panel.size = dimensions
	panel.color = color
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(panel)

func _load_preview(side: int) -> void:
	var vp := _viewport_nodes[side]
	if is_instance_valid(_models[side]):
		vp.remove_child(_models[side])
		_models[side].queue_free()
	_models[side] = null
	var source_path := CharacterRegistry.model_path(_ids[_indices[side]])
	if source_path.is_empty() or not ResourceLoader.exists(source_path):
		_status[side].text = "GLB NO DISPONIBLE"
		return
	var source := load(source_path) as PackedScene
	if source == null:
		_status[side].text = "ERROR EN MODELO"
		return
	var model := source.instantiate() as Node3D
	if model == null:
		_status[side].text = "ERROR EN ESCENA 3D"
		return
	# El personaje derecho se presenta mirando hacia su contrincante.
	# El rig GLB usa +X como frente (independiente del art_facing 2D).
	model.rotation.y = PI if side == 1 else 0.0
	vp.add_child(model)
	_models[side] = model
	var players := model.find_children("*", "AnimationPlayer", true, false)
	if not players.is_empty():
		var animator := players[0] as AnimationPlayer
		if animator.has_animation("idle"):
			animator.play("idle")
		else:
			_status[side].text = "SIN ANIMACION IDLE"

func _refresh_all() -> void:
	for side in 2:
		_names[side].text = CharacterRegistry.display_name(_ids[_indices[side]])
		_status[side].text = "CPU / ALEATORIO" if side == 1 and _is_cpu else ("LISTO" if _confirmed[side] else "ELEGIR + CONFIRMAR")
		_load_preview(side)
	_update_cards()
	_hints.text = "P1 WASD/U  ·  P2 FLECHAS/,  ·  ESC VOLVER" if not _is_cpu else "WASD CAMBIAR  ·  U CONFIRMAR  ·  ESC VOLVER"

func _update_cards() -> void:
	for i in _cards.size():
		var p1 := _indices[0] == i
		var p2 := _indices[1] == i
		var short_name: String = ["GUITARRA", "FRONTMAN", "OZZY", "BRUCE"][i] if i < 4 else _ids[i].to_upper()
		_cards[i].text = short_name + ("  1+2" if p1 and p2 else "  P1" if p1 else "  P2" if p2 else "")
		var accent := GOLD if p1 and p2 else CYAN if p1 else PINK if p2 else MUTED
		_cards[i].add_theme_color_override("font_color", accent if p1 or p2 else WHITE)
		_cards[i].add_theme_stylebox_override("normal", _card_style(accent, p1 or p2))

func _random_cpu() -> void:
	var alternatives := _ids.size() - 1
	_indices[1] = (_indices[0] + 1 + randi_range(0, alternatives - 1)) % _ids.size()
	_confirmed[1] = true

func _pick_card(index: int) -> void:
	var side := 0 if _is_cpu or not _confirmed[0] else 1
	# Mouse: primer clic selecciona, segundo confirma el personaje actual.
	if _indices[side] == index:
		_confirm(side)
	else:
		_move_selection(side, index)

func _move_selection(side: int, index: int) -> void:
	if _launching or _confirmed[side] or side == 1 and _is_cpu:
		return
	index = posmod(index, _ids.size())
	if _indices[side] == index:
		return
	_indices[side] = index
	_names[side].text = CharacterRegistry.display_name(_ids[index])
	_status[side].text = "ELEGIR + CONFIRMAR"
	_load_preview(side)
	_update_cards()

func _confirm(side: int) -> void:
	if _confirmed[side] or _launching or side == 1 and _is_cpu:
		return
	_confirmed[side] = true
	_status[side].text = "LISTO"
	if _is_cpu:
		_random_cpu()
		_status[1].text = "CPU / ALEATORIO"
		_names[1].text = CharacterRegistry.display_name(_ids[_indices[1]])
		_load_preview(1)
	if _confirmed[0] and _confirmed[1]:
		_launching = true
		GameConfig.set_characters(_ids[_indices[0]], _ids[_indices[1]])
		GameConfig.present_next_match = true
		get_tree().change_scene_to_file("res://match/match.tscn")

func _process(_delta: float) -> void:
	if _launching:
		return
	if Input.is_action_just_pressed("ui_cancel"):
		if _confirmed[0] and not _is_cpu:
			_confirmed[0] = false
			_status[0].text = "ELEGIR + CONFIRMAR"
		else:
			get_tree().change_scene_to_file("res://ui/main_menu.tscn")
		return
	_poll_player(0, "p1")
	if not _is_cpu:
		_poll_player(1, "p2")

func _poll_player(side: int, prefix: String) -> void:
	if _confirmed[side]:
		return
	var index := _indices[side]
	if Input.is_action_just_pressed(prefix + "_left"):
		index = (index + _ids.size() - 1) % _ids.size()
	elif Input.is_action_just_pressed(prefix + "_right"):
		index = (index + 1) % _ids.size()
	elif Input.is_action_just_pressed(prefix + "_up") or Input.is_action_just_pressed(prefix + "_down"):
		index = (index + 2) % _ids.size()
	_move_selection(side, index)
	if Input.is_action_just_pressed(prefix + "_lp") or Input.is_action_just_pressed(prefix + "_lk"):
		_confirm(side)
