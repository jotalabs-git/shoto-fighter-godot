extends Control
## Herramienta de desarrollo independiente. No se instancia desde el juego.
## Abrir res://dev/model_inspector.tscn con F6 o --path . res://dev/model_inspector.tscn

const MODEL_EXTENSIONS := ["glb", "gltf", "fbx", "obj", "blend"]
const SKIP_DIRS := [".git", ".godot", "addons", "test", "tests", "export", "build", "node_modules"]
const MAX_SCAN_DEPTH := 16
const MODEL_FOLDER := "res://assets/models"

var model_paths: Array[String] = []
var list: ItemList
var status: RichTextLabel
var details: Label
var viewport: SubViewport
var world: Node3D
var camera: Camera3D
var display_root: Node3D
var animation_player: AnimationPlayer
var animation_picker: OptionButton
var play_button: Button
var pause_button: Button
var stop_button: Button
var animation_entries: Array[Dictionary] = []
var yaw := 0.4
var pitch := 0.15
var distance := 3.5
var focus := Vector3.ZERO
var dragging := false


func _ready() -> void:
	get_window().title = "Rock Kombat | Inspector de modelos (DEV)"
	# El juego usa 384x216; esta escena necesita un lienzo de trabajo independiente.
	get_window().content_scale_size = Vector2i(1280, 720)
	get_window().size = Vector2i(1280, 720)
	get_window().min_size = Vector2i(900, 560)
	_build_interface()
	_build_world()
	_scan_models()


func _build_interface() -> void:
	var background := ColorRect.new()
	background.color = Color("#121725")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)

	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 8)
	add_child(root)

	var header := HBoxContainer.new()
	root.add_child(header)
	var title := Label.new()
	title.text = "  ROCK KOMBAT  /  INSPECTOR 3D  |  DEV"
	title.add_theme_font_size_override("font_size", 17)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var refresh := Button.new()
	refresh.text = "Volver a buscar"
	refresh.pressed.connect(_scan_models)
	header.add_child(refresh)
	var reset := Button.new()
	reset.text = "Centrar cámara"
	reset.pressed.connect(_frame_model)
	header.add_child(reset)

	var body := HSplitContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(body)

	var sidebar := VBoxContainer.new()
	sidebar.custom_minimum_size = Vector2(325, 0)
	body.add_child(sidebar)
	var heading := Label.new()
	heading.text = "MODELOS 3D"
	sidebar.add_child(heading)
	list = ItemList.new()
	list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	list.item_selected.connect(_on_model_selected)
	sidebar.add_child(list)
	var hint := Label.new()
	hint.text = "Carpeta: assets/models (incluye subcarpetas)\nArrastrar: rotar  |  Rueda: zoom"
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sidebar.add_child(hint)

	var right := VBoxContainer.new()
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(right)
	var container := SubViewportContainer.new()
	container.stretch = true
	container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	container.gui_input.connect(_on_viewport_input)
	right.add_child(container)
	var controls := HBoxContainer.new()
	right.add_child(controls)
	var anim_label := Label.new()
	anim_label.text = "Animación:"
	controls.add_child(anim_label)
	animation_picker = OptionButton.new()
	animation_picker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	animation_picker.item_selected.connect(_on_animation_selected)
	controls.add_child(animation_picker)
	play_button = Button.new()
	play_button.text = "▶ Reproducir"
	play_button.pressed.connect(_play_selected_animation)
	controls.add_child(play_button)
	pause_button = Button.new()
	pause_button.text = "⏸ Pausar"
	pause_button.pressed.connect(_toggle_animation_pause)
	controls.add_child(pause_button)
	stop_button = Button.new()
	stop_button.text = "⏹ Detener"
	stop_button.pressed.connect(_stop_animation)
	controls.add_child(stop_button)
	_refresh_animation_controls()
	viewport = SubViewport.new()
	viewport.size = Vector2i(960, 540)
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	viewport.own_world_3d = true
	container.add_child(viewport)
	details = Label.new()
	details.text = "Elegí un modelo para inspeccionarlo."
	details.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	right.add_child(details)
	status = RichTextLabel.new()
	status.bbcode_enabled = false
	status.scroll_active = true
	status.custom_minimum_size = Vector2(0, 42)
	root.add_child(status)
	_report("El inspector no modifica los modelos ni forma parte de la exportación del juego.")


func _build_world() -> void:
	world = Node3D.new()
	viewport.add_child(world)
	var environment := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("#293246")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.8, 0.85, 1.0)
	env.ambient_light_energy = 0.7
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	environment.environment = env
	world.add_child(environment)
	camera = Camera3D.new()
	camera.current = true
	camera.fov = 55.0
	world.add_child(camera)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45, -35, 0)
	light.light_energy = 1.7
	world.add_child(light)
	var rim := DirectionalLight3D.new()
	rim.rotation_degrees = Vector3(-30, 145, 0)
	rim.light_energy = 0.75
	world.add_child(rim)
	_update_camera()


func _scan_models() -> void:
	model_paths.clear()
	list.clear()
	# Solo assets/models y sus subdirectorios: no explorar el repositorio entero.
	if DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(MODEL_FOLDER)):
		_collect(MODEL_FOLDER, 0)
	model_paths.sort()
	for path in model_paths:
		list.add_item(path.trim_prefix(MODEL_FOLDER + "/"))
	_report("Encontrados %d modelos en %s" % [model_paths.size(), MODEL_FOLDER])
	if model_paths.is_empty():
		details.text = "No se encontraron modelos. Colocá los .glb en res://assets/models/ y presioná Volver a buscar."
	else:
		list.select(0)
		_on_model_selected(0)


func _collect(folder: String, depth: int) -> void:
	if depth > MAX_SCAN_DEPTH:
		return
	var dir := DirAccess.open(ProjectSettings.globalize_path(folder))
	if dir == null:
		return
	dir.list_dir_begin()
	var name := dir.get_next()
	while not name.is_empty():
		if not name.begins_with("."):
			var path := folder.path_join(name)
			if dir.current_is_dir():
				if name not in SKIP_DIRS:
					_collect(path, depth + 1)
			elif name.get_extension().to_lower() in MODEL_EXTENSIONS and not model_paths.has(path):
				model_paths.append(path)
		name = dir.get_next()
	dir.list_dir_end()


func _instantiate_model(path: String) -> Node3D:
	# GLB/GLTF sin importar: lectura directa, especialmente útil cuando se
	# acaban de copiar modelos al directorio desde un explorador de archivos.
	if path.get_extension().to_lower() in ["glb", "gltf"]:
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		var error := document.append_from_file(path, state)
		if error == OK:
			return document.generate_scene(state)
		_report("Error leyendo GLTF: %s (código %d)" % [path, error])
	var resource := ResourceLoader.load(path, "", ResourceLoader.CACHE_MODE_REPLACE)
	if resource is PackedScene:
		var instance := (resource as PackedScene).instantiate()
		if instance is Node3D:
			return instance as Node3D
		instance.free()
	return null


func _on_model_selected(index: int) -> void:
	if index < 0 or index >= model_paths.size():
		return
	var path := model_paths[index]
	_clear_model()
	var instance := _instantiate_model(path)
	if instance == null:
		details.text = "ERROR AL ABRIR: " + path
		_report("No se pudo cargar. Para OBJ/FBX/BLEND abrí antes el proyecto en el editor de Godot. Para GLB verificá que no esté corrupto y que sus archivos externos existan.")
		return
	display_root = Node3D.new()
	display_root.name = "LoadedModel"
	world.add_child(display_root)
	display_root.add_child(instance)
	var summary := _inspect_model(instance)
	_frame_model()
	details.text = "ARCHIVO: %s\n%s" % [path, summary]
	_report("Carga correcta: " + path)


func _clear_model() -> void:
	animation_player = null
	if is_instance_valid(display_root):
		display_root.free()
	display_root = null
	animation_entries.clear()
	_refresh_animation_controls()


func _inspect_model(root: Node) -> String:
	var stack: Array[Node] = [root]
	var meshes := 0
	var surfaces := 0
	var skeletons := 0
	var animations := 0
	animation_entries.clear()
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		if node is MeshInstance3D:
			meshes += 1
			if (node as MeshInstance3D).mesh != null:
				surfaces += (node as MeshInstance3D).mesh.get_surface_count()
		if node is Skeleton3D:
			skeletons += 1
		if node is AnimationPlayer:
			var player := node as AnimationPlayer
			if animation_player == null:
				animation_player = player
			for anim_name in player.get_animation_list():
				if anim_name == "RESET":
					continue
				animation_entries.append({"player": player, "name": anim_name})
				animations += 1
		for child in node.get_children():
			stack.append(child)
	_refresh_animation_controls()
	return "Meshes: %d  |  Superficies: %d  |  Esqueletos: %d  |  Animaciones disponibles: %d" % [meshes, surfaces, skeletons, animations]


func _refresh_animation_controls() -> void:
	if animation_picker == null:
		return
	animation_picker.clear()
	for entry in animation_entries:
		animation_picker.add_item(str(entry["name"]))
	var available := not animation_entries.is_empty()
	animation_picker.disabled = not available
	play_button.disabled = not available
	pause_button.disabled = not available
	stop_button.disabled = not available
	pause_button.text = "⏸ Pausar"
	if available:
		animation_picker.select(0)
	else:
		animation_picker.add_item("Sin animaciones")


func _selected_animation() -> Dictionary:
	if animation_picker == null:
		return {}
	var index := animation_picker.selected
	if index < 0 or index >= animation_entries.size():
		return {}
	return animation_entries[index]


func _on_animation_selected(_index: int) -> void:
	_play_selected_animation()


func _play_selected_animation() -> void:
	var entry := _selected_animation()
	if entry.is_empty():
		return
	# Si cambia el AnimationPlayer, detener el que estaba reproduciendo.
	for other in animation_entries:
		var other_player: AnimationPlayer = other["player"]
		if other_player != entry["player"]:
			other_player.stop()
	var player: AnimationPlayer = entry["player"]
	var name: StringName = entry["name"]
	player.play(name)
	pause_button.text = "⏸ Pausar"
	_report("Reproduciendo: %s" % name)


func _toggle_animation_pause() -> void:
	var entry := _selected_animation()
	if entry.is_empty():
		return
	var player: AnimationPlayer = entry["player"]
	if player.is_playing():
		player.pause()
		pause_button.text = "▶ Continuar"
		_report("Animación pausada: %s" % entry["name"])
	else:
		_play_selected_animation()


func _stop_animation() -> void:
	var entry := _selected_animation()
	if entry.is_empty():
		return
	var player: AnimationPlayer = entry["player"]
	player.stop()
	pause_button.text = "⏸ Pausar"
	_report("Animación detenida: %s" % entry["name"])


func _frame_model() -> void:
	yaw = 0.4
	pitch = 0.15
	var bounds := _get_bounds()
	if bounds.has("size"):
		focus = bounds["position"] + bounds["size"] * 0.5
		var radius: float = maxf((bounds["size"] as Vector3).length() * 0.5, 0.35)
		distance = maxf(radius / sin(deg_to_rad(camera.fov) * 0.5) * 1.55, 1.2)
	else:
		focus = Vector3.ZERO
		distance = 3.5
	_update_camera()


func _get_bounds() -> Dictionary:
	if not is_instance_valid(display_root):
		return {}
	var stack: Array[Node] = [display_root]
	var found := false
	var combined := AABB()
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
			var mesh_node := node as MeshInstance3D
			var local_box := mesh_node.get_aabb()
			for ix in 2:
				for iy in 2:
					for iz in 2:
						var point := local_box.position + local_box.size * Vector3(ix, iy, iz)
						var world_point := mesh_node.global_transform * point
						if not found:
							combined = AABB(world_point, Vector3.ZERO)
							found = true
						else:
							combined = combined.expand(world_point)
		for child in node.get_children():
			stack.append(child)
	if found:
		return {"position": combined.position, "size": combined.size}
	return {}


func _update_camera() -> void:
	if camera == null:
		return
	var direction := Vector3(
		sin(yaw) * cos(pitch),
		sin(pitch),
		cos(yaw) * cos(pitch)
	)
	camera.position = focus + direction * distance
	camera.look_at(focus, Vector3.UP)


func _on_viewport_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			dragging = event.pressed
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = maxf(distance * 0.87, 0.05)
			_update_camera()
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = minf(distance * 1.15, 10000.0)
			_update_camera()
	elif event is InputEventMouseMotion and dragging:
		yaw -= event.relative.x * 0.008
		pitch = clampf(pitch + event.relative.y * 0.008, -1.45, 1.45)
		_update_camera()


func _report(message: String) -> void:
	status.text = message
