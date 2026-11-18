class_name RoundPresenter
extends Node3D
## Stage-only puppet. Its movement and card follow the match's intro clock.

const SHOW_TICKS := 84
const WALK_CYCLE_METERS := 1.18
const WALK_SPEED := 2.45
const SIDE_CLEARANCE := 1.15
const TURN_TICKS := 17.0
const CARD_GRIP := Vector3(-.01, -.273, -.12)
const MODEL_PATH := "res://assets/models/presenter.glb"

var model: Node3D
var animation: AnimationPlayer
var rig: Skeleton3D
var card: Node3D
var number: Label3D
var walk_ticks := 70
var _route := WALK_CYCLE_METERS * 2.0
var _card_hand := -1
var _clip: StringName

func configure() -> bool:
	if not ResourceLoader.exists(MODEL_PATH, "PackedScene"):
		return false
	var source := load(MODEL_PATH) as PackedScene
	model = source.instantiate() as Node3D if source != null else null
	if model == null:
		return false
	add_child(model)
	var animations := model.find_children("*", "AnimationPlayer", true, false)
	var skeletons := model.find_children("*", "Skeleton3D", true, false)
	if animations.is_empty() or skeletons.is_empty():
		return false
	animation = animations[0]
	rig = skeletons[0]
	_card_hand = rig.find_bone("fist_far")
	if _card_hand < 0:
		return false
	for clip in [&"presenter_walk", &"presenter_show"]:
		if not animation.has_animation(clip) or animation.get_animation(clip).length <= 0.0:
			return false
	animation.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	_make_card()
	hide()
	return true

func set_stage_width(half_width: float) -> int:
	# Start and finish beyond the wings, including the width of the card.
	_route = half_width + SIDE_CLEARANCE
	walk_ticks = ceili(_route * 60.0 / WALK_SPEED)
	return walk_ticks * 2 + SHOW_TICKS

func sync(phase: int, tick: int, round_number: int, center: float) -> void:
	if phase != MatchState.INTRO:
		hide()
		return
	show()
	var walk_end := walk_ticks + SHOW_TICKS
	var walk_in := tick < walk_ticks
	var walk_out := tick >= walk_end
	var fraction := clampf(float(tick if walk_in else tick - walk_end) / walk_ticks, 0, 1)
	var x := 0.0
	if walk_in:
		x = lerpf(-_route, 0.0, fraction)
	elif walk_out:
		x = lerpf(0.0, _route, fraction)
	position = Vector3(center + x, .004, -.90)
	card.rotation.z = 0.0
	if walk_in or walk_out:
		var turn_fraction := TURN_TICKS / walk_ticks
		var turning := smoothstep(1.0 - turn_fraction, 1.0, fraction) if walk_in else 1.0 - smoothstep(0.0, turn_fraction, fraction)
		model.rotation.y = lerpf(-.22, -PI * .5, turning)
		# Anchor the gait phase at the center so both transitions meet the showcase pose.
		var seconds := fposmod(x / WALK_CYCLE_METERS, 1.0) * animation.get_animation(&"presenter_walk").length
		_sample(&"presenter_walk", seconds)
	else:
		model.rotation.y = -PI * .5
		var show_time := float(tick - walk_ticks) / SHOW_TICKS
		_sample(&"presenter_show", show_time * animation.get_animation(&"presenter_show").length)
		card.rotation.z = sin(TAU * show_time) * sin(PI * show_time) * .14
	rig.force_update_all_bone_transforms()
	var hand := to_local(rig.to_global(rig.get_bone_global_pose(_card_hand).origin))
	card.position = hand - card.basis * CARD_GRIP
	number.text = "ROUND %d" % round_number

func _sample(clip: StringName, seconds: float) -> void:
	if _clip != clip:
		_clip = clip
		animation.play(clip)
		animation.advance(0.0)
	animation.seek(seconds, true)

func _make_card() -> void:
	card = Node3D.new()
	add_child(card)
	_card_box(Vector3(.84, .40, .042), Vector3.ZERO, Color("#c38a55"))
	_card_box(Vector3(.79, .35, .024), Vector3(0, 0, .024), Color("#382143"))
	_card_box(Vector3(.082, .16, .074), Vector3(0, -.21, -.085), Color("#62384b"))
	number = Label3D.new()
	number.font_size = 54
	number.outline_size = 0
	number.pixel_size = .0032
	number.modulate = Color("#ffedbd")
	number.position.z = .041
	card.add_child(number)

func _card_box(size: Vector3, offset: Vector3, color: Color) -> void:
	var box := BoxMesh.new()
	box.size = size
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = .65
	box.material = material
	var detail := MeshInstance3D.new()
	detail.mesh = box
	detail.position = offset
	card.add_child(detail)
