class_name MatchManager
extends Node2D

## Orquestador del combate. Tras mover a los fighters aplica lo "global": paredes,
## pushbox, resolución de golpes (hitbox↔hurtbox) y cámara.
## (Rounds, timer, HUD y KO llegan en la Fase 6.)

@export var stage_left: float = -32.0
@export var stage_right: float = 416.0
@export var pushbox_min_sep: float = 44.0
@export var throw_range: float = 60.0
@export var view_width: float = 384.0
@export var cam_min_zoom: float = 0.70
@export var cam_max_zoom: float = 1.20
@export var cam_margin: float = 85.0
@export var cam_follow_speed: float = 5.0
@export var throw_closeup_zoom: float = 1.55
@export var throw_closeup_speed: float = 18.0
@export var throw_closeup_frames: int = 20
@export var p2_is_cpu: bool = false
@export var cpu_difficulty: String = "medium"
@export_enum("default", "3d", "sprites") var presentation_mode := "default"

@onready var camera: Camera2D = $Camera2D

const HIT_SPARK := preload("res://fx/hit_spark.tscn")

var p1: Fighter
var p2: Fighter
var hud: HUD = null
var match_state := MatchState.new()
var sfx: Sfx = null
var fighter_views: Combat3D
var _shake: int = 0
var _throw_closeup_remaining: int = 0
var _throw_was_active: bool = false
var _requested_3d := false

func _enter_tree() -> void:
	var cfg := get_node_or_null("/root/GameConfig")
	if cfg != null:
		# Asignar antes del _ready de los Fighter para cargar rig, stats y clips correctos.
		$Player1.character_id = cfg.p1_character_id
		$Player2.character_id = cfg.p2_character_id
	var mode: StringName = StringName(presentation_mode)
	if mode == &"default":
		mode = cfg.fighter_presentation if cfg != null else &"3d"
	_requested_3d = mode == &"3d" and not OS.get_cmdline_user_args().has("--sprites")
	if _requested_3d:
		for fighter: Fighter in [$Player1, $Player2]:
			fighter.defer_sprite_setup = true

func _ready() -> void:
	process_priority = 100   # correr DESPUÉS de que los fighters integren
	var cfg := get_node_or_null("/root/GameConfig")
	if cfg != null:
		p2_is_cpu = cfg.p2_is_cpu
		cpu_difficulty = cfg.cpu_difficulty
	sfx = Sfx.new()
	add_child(sfx)
	p1 = $Player1
	p2 = $Player2
	p1.opponent = p2
	p2.opponent = p1
	p1.team = 0
	p2.team = 1
	for f in [p1, p2]:
		f.wall_left = stage_left
		f.wall_right = stage_right
		f.attack_cued.connect(_on_attack_cued.bind(f))
		f.grab_cued.connect(_on_grab_cued.bind(f))
		f.throw_release_cued.connect(_on_throw_release)
		f.fall_cued.connect(_on_fall_cued)
	if p2_is_cpu:
		var ai := AIInput.new()
		ai.difficulty = cpu_difficulty
		ai.fighter = p2
		ai.opponent = p1
		p2.add_child(ai)
		p2.input_source = ai
	hud = get_node_or_null("HUD")
	if hud != null:
		hud.setup(p1, p2)
	_reset_round()
	if _requested_3d:
		var candidate := Combat3D.new()
		add_child(candidate)
		move_child(candidate, $ConcertStage.get_index() + 1)
		if candidate.configure(camera, [p1, p2]):
			fighter_views = candidate
		else:
			candidate.queue_free()
			for fighter in [p1, p2]:
				fighter._setup_sprite()

func _physics_process(delta: float) -> void:
	if p1 == null or p2 == null:
		return
	if Input.is_action_just_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://ui/main_menu.tscn")
		return
	if Input.is_action_just_pressed("toggle_debug"):
		var cfg := get_node_or_null("/root/GameConfig")
		if cfg != null:
			cfg.show_boxes = not cfg.show_boxes
	# Flujo de match (intro / pelea / fin de round / fin de match)
	var ev := match_state.tick(p1.health, p2.health)
	if ev == "next_round":
		_reset_round()
	elif ev == "fight" and sfx != null:
		sfx.play_announcer("fight")
	elif ev == "round_end":
		for fighter in [p1, p2]:
			if fighter.health <= 0 and fighter.state_machine.current_state.name != &"Knockdown":
				fighter.begin_knockdown(&"normal")
		if sfx != null:
			sfx.play_ko()
	elif ev == "match_end" and sfx != null:
		sfx.play_announcer("winner")
	# Pueden actuar en intro y pelea; se congelan en fin de round / fin de match.
	var can_act := match_state.phase == MatchState.FIGHT or match_state.phase == MatchState.INTRO
	if not can_act:
		p1.cancel_throw_victim()
		p2.cancel_throw_victim()
	p1.frozen = not can_act
	p2.frozen = not can_act
	# Pushbox + paredes (siempre)
	var sep := StagePhysics.separate(p1.position.x, p2.position.x, pushbox_min_sep)
	p1.position.x = sep[0]
	p2.position.x = sep[1]
	p1.position.x = StagePhysics.clamp_wall(p1.position.x, stage_left, stage_right)
	p2.position.x = StagePhysics.clamp_wall(p2.position.x, stage_left, stage_right)
	# Agarres y golpes durante intro/pelea
	if can_act:
		Throws.resolve(p1, p2, throw_range)
		if Combat.resolve(p1, p2):
			_on_hit(p2, p1, p1.current_move, _is_blocking_hit(p2))
		if Combat.resolve(p2, p1):
			_on_hit(p1, p2, p2.current_move, _is_blocking_hit(p1))
	# Solo un agarre efectivo inicia la toma; throw tech nunca entra a Throw.
	var throwing := _is_throwing()
	if throwing and not _throw_was_active:
		_throw_closeup_remaining = throw_closeup_frames
	_throw_was_active = throwing
	# Proyectiles
	_process_projectiles(delta)
	# Cámara
	if camera != null:
		var cam := CameraLogic.compute(p1.position.x, p2.position.x, view_width, cam_min_zoom, cam_max_zoom, cam_margin)
		var closeup := _throw_closeup_remaining > 0
		if closeup:
			var close_zoom := minf(throw_closeup_zoom, 1.38) if fighter_views != null else throw_closeup_zoom
			cam = CameraLogic.throw_closeup(p1.position.x, p2.position.x, close_zoom)
			_throw_closeup_remaining -= 1
		var off := 0.0
		if _shake > 0:
			off = 5.0 if (_shake % 2 == 0) else -5.0
			_shake -= 1
		# Acerca la cámara al pelear juntos y la aleja al retroceder.
		# Interpolación exponencial para evitar saltos con FPS variables.
		var speed := throw_closeup_speed if closeup else cam_follow_speed
		var follow := 1.0 - exp(-speed * delta)
		camera.position.x = lerpf(camera.position.x, float(cam[0]), follow) + off
		var target_y := (119.0 if fighter_views != null else 126.0) if closeup else 108.0
		camera.position.y = lerpf(camera.position.y, target_y, follow)
		var zoom := lerpf(camera.zoom.x, float(cam[1]), follow)
		camera.zoom = Vector2(zoom, zoom)
	_update_hud()
	if match_state.match_over() and _rematch_pressed():
		match_state.reset_match()
		_reset_round()

## Se utiliza el estado real del atacante para no activar el primer plano
## ante un intento fallido o un agarre neutralizado (throw tech).
func _is_throwing() -> bool:
	for fighter in [p1, p2]:
		if fighter.state_machine.current_state != null and fighter.state_machine.current_state.name == "Throw":
			return true
	return false

func _reset_round() -> void:
	if sfx != null:
		var round_num := mini(match_state.p1_rounds + match_state.p2_rounds + 1, 3)
		sfx.play_announcer("round_" + str(round_num))
	_throw_closeup_remaining = 0
	_throw_was_active = false
	p1.reset_for_round(Vector2(112.0, 180.0), true)
	p2.reset_for_round(Vector2(272.0, 180.0), false)
	if camera != null:
		# Nuevo round: iniciar con el encuadre correcto, sin zoom progresivo
		# desde una posición heredada del round anterior.
		var cam := CameraLogic.compute(p1.position.x, p2.position.x, view_width, cam_min_zoom, cam_max_zoom, cam_margin)
		camera.position.x = cam[0]
		camera.position.y = 108.0
		camera.zoom = Vector2(cam[1], cam[1])
	for proj in get_tree().get_nodes_in_group("projectile"):
		proj.queue_free()

func _update_hud() -> void:
	if hud == null:
		return
	hud.set_timer(match_state.timer_seconds())
	hud.set_rounds(match_state.p1_rounds, match_state.p2_rounds)
	var msg := ""
	match match_state.phase:
		MatchState.INTRO:
			msg = "ROUND %d" % (match_state.p1_rounds + match_state.p2_rounds + 1)
		MatchState.ROUND_END:
			msg = "K.O." if (p1.health <= 0 or p2.health <= 0) else "TIME UP"
		MatchState.MATCH_END:
			var w := match_state.match_winner()
			msg = ("PLAYER 1 WINS" if w == 1 else "PLAYER 2 WINS") + "  ·  attack to rematch"
	hud.set_message(msg)

func _rematch_pressed() -> bool:
	for a in ["p1_lp", "p1_mp", "p1_hp", "p2_lp", "p2_mp", "p2_hp"]:
		if Input.is_action_just_pressed(a):
			return true
	return false

func _on_attack_cued(move: MoveData, fighter: Fighter) -> void:
	if sfx != null:
		sfx.play_attack(fighter, move)

func _on_grab_cued(fighter: Fighter) -> void:
	if sfx != null:
		sfx.play_grab(fighter)

func _on_throw_release() -> void:
	if sfx != null:
		sfx.play_hit()

func _on_fall_cued(character_id: String) -> void:
	if sfx != null:
		sfx.play_fall(character_id)

func _is_blocking_hit(defender: Fighter) -> bool:
	return defender.state_machine.current_state != null and defender.state_machine.current_state.name == "Blockstun"

func _on_hit(defender: Fighter, attacker: Fighter = null, move: MoveData = null, blocked: bool = false) -> void:
	_spawn_spark(defender.global_position + Vector2(0.0, -50.0))
	_shake = 9
	if sfx != null:
		sfx.play_impact(attacker, defender, move, blocked)

func _spawn_spark(pos: Vector2) -> void:
	var spark := HIT_SPARK.instantiate()
	spark.global_position = pos
	add_child(spark)

func _process_projectiles(delta: float) -> void:
	for proj in get_tree().get_nodes_in_group("projectile"):
		proj.position.x += proj.velocity_x * delta
		if proj.position.x < stage_left - 80.0 or proj.position.x > stage_right + 80.0:
			proj.queue_free()
			continue
		for f in [p1, p2]:
			if f.team == proj.team or f.is_invulnerable():
				continue
			if proj.rect().intersects(f.hurtbox_rect()):
				if f.is_blocking(proj.move):
					f.receive_block(proj.move, proj.owner_facing)
				else:
					f.receive_hit(proj.move, proj.owner_facing)
				_on_hit(f, null, proj.move, _is_blocking_hit(f))
				proj.queue_free()
				break
