class_name Fighter3DView
extends Node3D
## Model space: +X faces forward, +Y is up. Only this view moves during a grip.

const UNITS_PER_METER := 34.0
const FPS := 60.0
const REQUIRED_CLIPS := [
	"crouch_enter", "crouch_exit", "jump_start", "jump", "fall_air", "land",
	"idle", "block_high", "block_low", "grabbed_hold", "thrown_air", "throw",
	"knockdown", "knockdown_low", "down_hold", "getup", "ko_fall",
	"walk_fwd", "walk_back", "run", "run_back",
]
const AIR_NORMALS := {
	"j.lp": "jump_lp", "j.mp": "jump_mp", "j.hp": "jump_hp",
	"j.lk": "jump_lk", "j.mk": "jump_mk", "j.hk": "jump_hk",
	"cr.hp": "crouch_hp", "cr.mk": "crouch_mk",
}
static var _clay_texture: NoiseTexture2D
static var _clay_materials := {}

var fighter: Fighter
var skeleton: Skeleton3D
var player: AnimationPlayer
var clips: Dictionary
var clip: StringName
var sampled_tick := 0.0
var grip_offset := Vector3.ZERO
var _release_offset := Vector3.ZERO
var _was_held := false
var _last_state: StringName
var _last_ground := true
var _elapsed := 0.0
var _transition: StringName
var _last_reset := -1
var _last_x := 0.0
var _travel := 0.0
var _down_floor_offset := 0.0

static func to_world(point: Vector2, floor_y: float) -> Vector3:
	return Vector3(point.x, floor_y - point.y, 0.0) / UNITS_PER_METER

func load_model(character_id: String) -> bool:
	var base := "res://assets/models/" + character_id
	var source := load(base + ".glb") as PackedScene if ResourceLoader.exists(base + ".glb") else null
	var catalog := FileAccess.open(base + ".json", FileAccess.READ)
	if source == null or catalog == null:
		return false
	var data = JSON.parse_string(catalog.get_as_text())
	if not data is Dictionary or not data.get("clips") is Dictionary:
		return false
	var model := source.instantiate() as Node3D
	if model == null:
		return false
	add_child(model)
	var skeletons := model.find_children("*", "Skeleton3D", true, false)
	var players := model.find_children("*", "AnimationPlayer", true, false)
	if players.is_empty() or skeletons.is_empty():
		return false
	skeleton = skeletons[0] as Skeleton3D
	for bone in ["pelvis", "fist_near", "fist_far"]:
		if skeleton.find_bone(bone) < 0:
			return false
	player = players[0] as AnimationPlayer
	clips = data["clips"]
	for required in REQUIRED_CLIPS:
		if not clips.has(required):
			return false
	_down_floor_offset = float(data.get("down_floor_offset", 0.0))
	for anim in clips:
		if not clips[anim] is Dictionary or float(clips[anim].get("ticks", 0.0)) <= 0.0 \
				or not player.has_animation(anim) or player.get_animation(anim).get_track_count() == 0 \
				or player.get_animation(anim).length <= 0.0:
			return false
	for gait in ["walk_fwd", "walk_back", "run", "run_back"]:
		if float(clips[gait].get("travel", 0.0)) <= 0.0:
			return false
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	if DisplayServer.get_name() != "headless" and not is_software_rendering():
		_add_clay_finish(model)
	return true

static func is_software_rendering() -> bool:
	var adapter := RenderingServer.get_video_adapter_name().to_lower()
	return adapter.contains("llvmpipe") or adapter.contains("softpipe")

func _add_clay_finish(model: Node3D) -> void:
	# glTF carries the base colors and roughness. Use a small shared triplanar
	# normal map for the hand-worked clay grain from Blender's procedural finish.
	if _clay_texture == null:
		var noise := FastNoiseLite.new()
		noise.frequency = 0.085
		noise.fractal_octaves = 3
		_clay_texture = NoiseTexture2D.new()
		_clay_texture.width = 256
		_clay_texture.height = 256
		_clay_texture.seamless = true
		_clay_texture.as_normal_map = true
		_clay_texture.noise = noise
	for mesh: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		for index in mesh.get_surface_override_material_count():
			var material := mesh.get_active_material(index) as StandardMaterial3D
			if material == null or material.normal_enabled or material.metallic > 0.3:
				continue
			if not _clay_materials.has(material):
				var clay := material.duplicate() as StandardMaterial3D
				clay.uv1_triplanar = true
				clay.uv1_scale = Vector3(4.5, 4.5, 4.5)
				clay.normal_enabled = true
				clay.normal_texture = _clay_texture
				clay.normal_scale = 0.18
				_clay_materials[material] = clay
			mesh.set_surface_override_material(index, _clay_materials[material])

func sample(name: StringName, tick: float) -> void:
	if not clips.has(name):
		name = &"idle"
	var length := float(clips[name]["ticks"])
	if clips[name]["loop"]:
		tick = fposmod(tick, length)
	sampled_tick = clampf(tick, 0.0, length)
	if clip != name:
		clip = name
		player.play(clip)
		player.advance(0.0)
	player.seek(minf(sampled_tick / FPS, player.get_animation(clip).length), true)
	skeleton.force_update_all_bone_transforms()

func sync(delta: float, held_tick: int = -1) -> void:
	var state: State = fighter.state_machine.current_state
	var name := state.name
	if _last_reset != fighter.visual_round_revision:
		_last_reset = fighter.visual_round_revision
		_last_state = &""
		_last_ground = true
		_transition = &""
		grip_offset = Vector3.ZERO
		_release_offset = Vector3.ZERO
		_was_held = false
	if name != _last_state:
		_elapsed = 0.0
		_travel = 0.0
		_last_x = fighter.global_position.x
		_transition = &""
		if name == &"Idle":
			if not _last_ground or _last_state == &"Jump" or (_last_state == &"Attack" and clip.begins_with("jump_")):
				_transition = &"land"
			elif _last_state == &"Crouch":
				_transition = &"crouch_exit"
	if fighter.hitstop_frames == 0 and not fighter.frozen:
		_elapsed += delta * FPS
	_last_state = name
	_last_ground = fighter.on_ground
	_travel += absf(fighter.global_position.x - _last_x) / UNITS_PER_METER
	_last_x = fighter.global_position.x
	position = to_world(fighter.global_position, fighter.ground_y)
	rotation.y = deg_to_rad(-12.0) if fighter.facing() > 0 else deg_to_rad(192.0)
	var tick := float(state.state_frame)
	match name:
		&"Throw":
			sample(&"throw", tick)
		&"Thrown":
			sample(&"grabbed_hold", maxf(held_tick, 0))
		&"Knockdown":
			var fall := &"thrown_air" if fighter.knockdown_style == &"throw" else (&"knockdown_low" if fighter.knockdown_style == &"low" else &"knockdown")
			if fighter.health <= 0:
				tick = float(fighter.ko_ticks)
				if fighter.knockdown_style != &"throw":
					fall = &"ko_fall"
				position.y *= 1.0 - clampf(tick / float(fighter.fall_contact_tick()), 0.0, 1.0)
			var authored_ticks := float(clips[fall]["ticks"])
			var impact := float(clips[fall].get("ground_contact", authored_ticks))
			var contact := float(fighter.fall_contact_tick())
			position.y += _down_floor_offset * smoothstep(4.0, contact, tick)
			var pose_tick := tick * impact / contact if tick < contact else impact + tick - contact
			if pose_tick >= authored_ticks and (fighter.on_ground or fighter.health <= 0):
				sample(&"down_hold", 0)
			else:
				sample(fall, pose_tick)
		&"Getup":
			position.y += _down_floor_offset * (1.0 - smoothstep(0.0, 8.0, tick))
			sample(&"getup", tick * float(clips["getup"]["ticks"]) / Fighter.GETUP_FRAMES)
		&"Attack":
			var move := fighter.current_move
			if move == null:
				sample(&"idle", _elapsed)
				return
			var attack_clip: StringName = AIR_NORMALS.get(move.move_name.to_lower(), fighter._attack_anim())
			sample(attack_clip, _attack_tick(move, clips.get(attack_clip, clips["idle"]), tick))
		&"JumpStartup":
			sample(&"jump_start", tick)
		&"Jump":
			sample(&"jump" if fighter.vel.y < 0.0 else &"fall_air", tick if fighter.vel.y < 0.0 else maxf(tick - 16.0, 0.0))
		&"Crouch":
			sample(&"crouch_enter" if tick < 5.0 else &"crouch", tick)
		&"Walk", &"Dash":
			var moving_forward := signf(fighter.vel.x) == float(fighter.facing())
			var gait := &"walk_fwd" if moving_forward else &"walk_back"
			if name == &"Dash":
				gait = &"run" if moving_forward else &"run_back"
			var data: Dictionary = clips[gait]
			sample(gait, _travel * float(data["ticks"]) / float(data["travel"]))
		&"Blockstun":
			if tick < 6.0:
				sample(&"block_low" if fighter.input.down else &"block_high", tick)
			else:
				sample(&"guard_crouch" if fighter.input.down else &"guard", 0)
		&"Hitstun":
			sample(&"hurt_low" if fighter.last_hit_low else &"hurt", tick)
		&"Idle":
			if _transition != &"" and _elapsed < float(clips[_transition]["ticks"]):
				sample(_transition, _elapsed)
			else:
				sample(&"idle", _elapsed)
		_:
			sample(fighter._sprite_anim(name), tick)

func _attack_tick(move: MoveData, info: Dictionary, tick: float) -> float:
	if not info.has("impact"):
		return tick
	var impact := float(info["impact"])
	var recovery := float(info["recovery"])
	var start := float(move.startup)
	var active := float(move.active)
	if tick < start:
		return lerpf(0.0, impact, tick / maxf(start, 1.0))
	if tick < start + active:
		return lerpf(impact, recovery, (tick - start) / maxf(active, 1.0))
	return lerpf(recovery, float(info["ticks"]), (tick - start - active) / maxf(move.recovery, 1.0))

func _bone_point(name: String, offset: Vector3 = Vector3.ZERO) -> Vector3:
	var index := skeleton.find_bone(name)
	return skeleton.global_transform * (skeleton.get_bone_global_pose(index) * offset)

func align_grip(attacker: Fighter3DView, tick: int) -> void:
	# In GLTF bone-local Y follows the spine. Both wrists share one contact target.
	var hands := (attacker._bone_point("fist_near") + attacker._bone_point("fist_far")) * 0.5
	var forward := attacker.transform.basis.x
	var target := hands + forward * 0.12
	var chest := _bone_point("pelvis", Vector3(0, 0.49, 0))
	var grip := target - chest
	grip.x = clampf(grip.x, -0.78, 0.78)
	grip.y = clampf(grip.y, -0.18, 0.62)
	grip.z = clampf(grip.z, -0.33, 0.33)
	grip_offset = grip * smoothstep(1.0, 5.0, float(tick))
	position += grip_offset
	_was_held = true

func finish_grip() -> void:
	var state := fighter.state_machine.current_state
	var thrown := state.name == &"Knockdown" and fighter.knockdown_style == &"throw"
	if _was_held:
		_release_offset = grip_offset if thrown else Vector3.ZERO
		_was_held = false
	grip_offset = Vector3.ZERO
	if thrown:
		var tick := fighter.ko_ticks if fighter.health <= 0 else state.state_frame
		# Vertical offset clears before the authored body reaches the floor.
		grip_offset = _release_offset * (1.0 - smoothstep(0.0, 7.0, float(tick)))
		position += grip_offset
	else:
		_release_offset = Vector3.ZERO
