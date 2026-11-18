extends Node3D
## Standalone animation browser. Model time follows the exported clip catalog.

const SOLO_MODELS := {"ozzy": "Ozzy", "bruce": "Bruce Dickinson"}

var views: Array[Fighter3DView] = []
var names: PackedStringArray
var selected := 0
var time := 0.0
var png: Array[TextureRect] = []
var reference := false
var solo_id := ""

func _ready() -> void:
	for id: String in SOLO_MODELS:
		if OS.get_cmdline_user_args().has("--" + id):
			solo_id = id
			break
	var ids := [solo_id] if not solo_id.is_empty() else ["guitarist", "frontman"]
	var overlay := CanvasLayer.new()
	add_child(overlay)
	for index in ids.size():
		var id: String = ids[index]
		var view := Fighter3DView.new()
		add_child(view)
		if not view.load_model(id):
			push_error("No se pudo importar " + id)
			get_tree().quit(1)
			return
		views.append(view)
		if not solo_id.is_empty():
			$Camera.size = 3.65
			view.rotation.y = -1.02
			continue
		view.position.x = -1.6 if index == 0 else 1.6
		view.rotation.y = -0.22 if index == 0 else 3.36
		var texture := TextureRect.new()
		texture.position = Vector2(45 + index * 190, 35)
		texture.size = Vector2(110, 145)
		texture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		texture.mouse_filter = Control.MOUSE_FILTER_IGNORE
		overlay.add_child(texture)
		png.append(texture)
	names = views[0].player.get_animation_list()
	if names.has("RESET"):
		names.remove_at(names.find("RESET"))
	_refresh()

func _process(delta: float) -> void:
	if names.is_empty():
		return
	time += delta
	for view in views:
		view.sample(names[selected], fposmod(time * 60.0, float(view.clips[names[selected]]["ticks"])))

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_RIGHT:
			selected = (selected + 1) % names.size()
		KEY_LEFT:
			selected = posmod(selected - 1, names.size())
		KEY_P:
			if not solo_id.is_empty():
				return
			reference = not reference
		KEY_A, KEY_D:
			if not solo_id.is_empty():
				views[0].rotation.y += -.30 if event.keycode == KEY_A else .30
			return
		KEY_ESCAPE:
			get_tree().quit()
			return
		_:
			return
	time = 0.0
	_refresh()

func _refresh() -> void:
	if not solo_id.is_empty():
		$HUD/Clip.text = SOLO_MODELS[solo_id] + "  /  " + names[selected] + "\n← / → clip   A / D girar   Esc salir"
		return
	$HUD/Clip.text = names[selected] + "\n← / → clip   P alterna PNG   Esc salir"
	for index in 2:
		var id := "guitarist" if index == 0 else "frontman"
		var frames := CharacterFrames.get_frames(id)
		var name := names[selected] if frames.has_animation(names[selected]) else "idle"
		png[index].texture = frames.get_frame_texture(name, 0)
		png[index].visible = reference
		views[index].visible = not reference
