class_name Combat3D
extends Node2D
## A single transparent 3D pass between the stage and 2D combat effects.

const LOGICAL_SIZE := Vector2(384, 216)
const MAX_WIDTH := 1920.0

var viewport_3d: SubViewport
var camera_3d: Camera3D
var camera_2d: Camera2D
var surface: Sprite2D
var models: Array[Fighter3DView] = []
var presenter: RoundPresenter
var _match_state: MatchState
var _window_size := Vector2i.ZERO
var _old_visibility: Array[Vector2i] = []
var _max_width := MAX_WIDTH

func configure(camera: Camera2D, fighters: Array[Fighter]) -> bool:
	camera_2d = camera
	process_priority = 120
	viewport_3d = SubViewport.new()
	viewport_3d.own_world_3d = true
	viewport_3d.transparent_bg = true
	if Fighter3DView.is_software_rendering():
		_max_width = 960.0
	else:
		viewport_3d.msaa_3d = Viewport.MSAA_2X
	viewport_3d.render_target_update_mode = SubViewport.UPDATE_DISABLED if DisplayServer.get_name() == "headless" else SubViewport.UPDATE_ALWAYS
	add_child(viewport_3d)

	camera_3d = Camera3D.new()
	camera_3d.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera_3d.near = 0.1
	camera_3d.far = 80.0
	camera_3d.current = true
	viewport_3d.add_child(camera_3d)

	var world := WorldEnvironment.new()
	var environment := Environment.new()
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.87, 0.91, 1.0)
	environment.ambient_light_energy = 0.52
	world.environment = environment
	viewport_3d.add_child(world)
	_light(Vector3(-0.45, -0.75, -0.6), Color(1.0, 0.87, 0.76), 1.05)
	_light(Vector3(0.7, -0.25, -0.8), Color(0.69, 0.8, 1.0), 0.48)
	_light(Vector3(0.0, -0.7, 0.7), Color(0.99, 0.65, 0.61), 0.7)

	for fighter in fighters:
		var view := Fighter3DView.new()
		view.fighter = fighter
		viewport_3d.add_child(view)
		if not view.load_model(fighter.character_id):
			return false
		models.append(view)

	surface = Sprite2D.new()
	surface.centered = false
	surface.texture = viewport_3d.get_texture()
	surface.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(surface)
	for view in models:
		var fighter := view.fighter
		_old_visibility.append(Vector2i(int(fighter.sprite.visible), int(fighter.visual.visible)))
		fighter.sprite.hide()
		fighter.visual.hide()
	_process(0.0)
	return true

func add_round_presenter(state: MatchState) -> bool:
	var actor := RoundPresenter.new()
	viewport_3d.add_child(actor)
	if not actor.configure():
		actor.queue_free()
		return false
	presenter = actor
	_match_state = state
	return true

func _exit_tree() -> void:
	for index in _old_visibility.size():
		var fighter := models[index].fighter
		if is_instance_valid(fighter) and is_instance_valid(fighter.sprite):
			fighter.sprite.visible = bool(_old_visibility[index].x)
			fighter.visual.visible = bool(_old_visibility[index].y)

func _light(direction: Vector3, color: Color, energy: float) -> void:
	var light := DirectionalLight3D.new()
	light.light_color = color
	light.light_energy = energy
	viewport_3d.add_child(light)
	light.look_at_from_position(-direction, Vector3.ZERO)

func _process(delta: float) -> void:
	if surface == null:
		return
	var logical_size := get_viewport_rect().size
	var size := get_window().size
	if size != _window_size:
		_window_size = size
		var width := clampf(float(size.x), LOGICAL_SIZE.x, _max_width)
		viewport_3d.size = Vector2i(roundi(width), roundi(width * logical_size.y / logical_size.x))
		surface.scale = logical_size / Vector2(viewport_3d.size)
	# The texture samples the same logical screen rectangle as the Camera2D.
	global_transform = get_viewport().get_canvas_transform().affine_inverse()
	var center := Fighter3DView.to_world(camera_2d.get_screen_center_position(), models[0].fighter.ground_y)
	camera_3d.position = center + Vector3(0, 0, 13.0)
	camera_3d.size = logical_size.y / (Fighter3DView.UNITS_PER_METER * camera_2d.zoom.y)
	if presenter != null:
		var middle := (models[0].fighter.position.x + models[1].fighter.position.x) / 2.0
		presenter.sync(_match_state.phase, _match_state.phase_frame,
			_match_state.p1_rounds + _match_state.p2_rounds + 1, middle / Fighter3DView.UNITS_PER_METER)

	for view in models:
		var rival := models[1] if view == models[0] else models[0]
		var held := rival.fighter.throw_victim == view.fighter
		var tick := rival.fighter.state_machine.current_state.state_frame if held else -1
		view.sync(delta, tick)
	for view in models:
		var rival := models[1] if view == models[0] else models[0]
		if rival.fighter.throw_victim == view.fighter:
			view.align_grip(rival, rival.fighter.state_machine.current_state.state_frame)
		else:
			view.finish_grip()
