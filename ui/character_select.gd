extends Control
## Arcade roster: two independent selections with live, standing GLB previews.
## The fighting rules stay in Fighter and MatchManager.

const IDS := ["guitarist", "frontman", "ozzy", "bruce"]
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
	_is_cpu = GameConfig.p2_is_cpu
	_indices[0] = maxi(IDS.find(GameConfig.p1_character_id), 0)
	_indices[1] = maxi(IDS.find(GameConfig.p2_character_id), 0)
	if _is_cpu:
		_random_cpu()
	_construct()
	_refresh_all()

func _construct() -> void:
	var bg := ColorRect.new()
	bg.color = BG
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_label("ROCK KOMBAT", Vector2(0, 3), Vector2(384, 23), 18, GOLD, HORIZONTAL_ALIGNMENT_CENTER)
	_label("ELEGÍ TU LUCHADOR", Vector2(0, 25), Vector2(384, 14), 9, MUTED, HORIZONTAL_ALIGNMENT_CENTER)
	_label("P1", Vector2(11, 42), Vector2(100, 16), 12, CYAN)
	_label("CPU" if _is_cpu else "P2", Vector2(273, 42), Vector2(100, 16), 12, PINK, HORIZONTAL_ALIGNMENT_RIGHT)

	for side in 2:
		var x := 5.0 if side == 0 else 259.0
		_panel(Vector2(x, 58), Vector2(120, 112), Color("#181A2D"))
		_add_preview(side, Vector2(x + 1.0, 59.0))
		var name := _label("", Vector2(x, 172), Vector2(120, 15), 9, CYAN if side == 0 else PINK, HORIZONTAL_ALIGNMENT_CENTER)
		_names.append(name)
		var status := _label("", Vector2(x, 188), Vector2(120, 13), 8, MUTED, HORIZONTAL_ALIGNMENT_CENTER)
		_status.append(status)

	_label("SELECCIÓN", Vector2(131, 43), Vector2(122, 15), 10, WHITE, HORIZONTAL_ALIGNMENT_CENTER)
	for index in IDS.size():
		var b := Button.new()
		b.text = CharacterRegistry.display_name(IDS[index]).replace("EL ", "").replace(" DICKINSON", "")
		b.position = Vector2(133.0 + float(index % 2) * 62.0, 64.0 + float(index / 2) * 52.0)
		b.size = Vector2(59, 49)
		b.add_theme_font_size_override("font_size", 9)
		b.add_theme_color_override("font_color", WHITE)
		b.add_theme_stylebox_override("normal", RockBrand.button_style())
		b.add_theme_stylebox_override("hover", RockBrand.button_style(true))
		b.pressed.connect(_pick_card.bind(index))
		add_child(b)
		_cards.append(b)
	_hints = _label("", Vector2(7, 202), Vector2(370, 13), 8, MUTED, HORIZONTAL_ALIGNMENT_CENTER)

func _add_preview(side: int, at: Vector2) -> void:
	var holder := SubViewportContainer.new()
	holder.position = at
	holder.size = Vector2(118, 110)
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
	camera.look_at(Vector3(0, 1.27, 0), Vector3.UP)
	camera.current = true
	vp.add_child(camera)

	for index in 2:
		var light := DirectionalLight3D.new()
		light.light_color = (Color("#FFF0D9") if index == 0 else Color("#A4CFFF"))
		light.light_energy = 1.25 if index == 0 else 0.65
		if index == 0:
			light.rotation_degrees = Vector3(-38, -35 if side == 0 else 35, 0)
		else:
			light.rotation_degrees = Vector3(-20, 120, 0)
		vp.add_child(light)

func _label(value: String, pos: Vector2, dimensions: Vector2, font_size: int, color: Color, horizontal: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var label := Label.new()
	label.text = value
	label.position = pos
	label.size = dimensions
	label.horizontal_alignment = horizontal
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
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
	var source_path := CharacterRegistry.model_path(IDS[_indices[side]])
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
		_names[side].text = CharacterRegistry.display_name(IDS[_indices[side]])
		_status[side].text = "CPU / ALEATORIO" if side == 1 and _is_cpu else ("LISTO" if _confirmed[side] else "ELEGIR + CONFIRMAR")
		_load_preview(side)
	_update_cards()
	_hints.text = "P1 WASD + U  /  P2 FLECHAS + ,  /  ESC VOLVER" if not _is_cpu else "WASD CAMBIAR  ·  U CONFIRMAR  ·  ESC VOLVER"

func _update_cards() -> void:
	for i in _cards.size():
		var p1 := _indices[0] == i
		var p2 := _indices[1] == i
		var marker := ("1" if p1 else "") + ("2" if p2 else "")
		_cards[i].text = CharacterRegistry.display_name(IDS[i]).replace("EL ", "").replace(" DICKINSON", "") + ("  [" + marker + "]" if marker != "" else "")
		_cards[i].add_theme_color_override("font_color", GOLD if p1 and p2 else CYAN if p1 else PINK if p2 else WHITE)

func _random_cpu() -> void:
	var alternatives := IDS.size() - 1
	_indices[1] = (_indices[0] + 1 + randi_range(0, alternatives - 1)) % IDS.size()
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
	index = posmod(index, IDS.size())
	if _indices[side] == index:
		return
	_indices[side] = index
	_names[side].text = CharacterRegistry.display_name(IDS[index])
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
		_names[1].text = CharacterRegistry.display_name(IDS[_indices[1]])
		_load_preview(1)
	if _confirmed[0] and _confirmed[1]:
		_launching = true
		GameConfig.set_characters(IDS[_indices[0]], IDS[_indices[1]])
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
		index = (index + IDS.size() - 1) % IDS.size()
	elif Input.is_action_just_pressed(prefix + "_right"):
		index = (index + 1) % IDS.size()
	elif Input.is_action_just_pressed(prefix + "_up") or Input.is_action_just_pressed(prefix + "_down"):
		index = (index + 2) % IDS.size()
	_move_selection(side, index)
	if Input.is_action_just_pressed(prefix + "_lp") or Input.is_action_just_pressed(prefix + "_lk"):
		_confirm(side)
