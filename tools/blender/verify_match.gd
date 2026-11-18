extends SceneTree
## End-to-end screenshot and combat smoke test using the shipped match and InputMap.

var output: String
var cpu: bool
var slice: bool
var round_test: bool
var views := {}

func _initialize() -> void:
	call_deferred("_verify")

func _verify() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		printerr("Uso: verify_match.gd -- DIRECTORIO [--sprites] [--cpu] [--slice] [--round] [--match] [--throws] [--ko] [--arms]")
		quit(2)
		return
	output = ProjectSettings.globalize_path(args[0])
	cpu = args.has("--cpu")
	slice = args.has("--slice")
	round_test = args.has("--round")
	DirAccess.make_dir_recursive_absolute(output)
	seed(13)
	var cfg := root.get_node("GameConfig")
	cfg.set_mode(cpu, "medium")
	# Resolve the match script after autoloads are ready in command-line runs.
	var arena: Node = load("res://match/match.tscn").instantiate()
	if slice:
		arena.presentation_mode = "sprites"
	root.add_child(arena)
	# Fixed simulation steps can outrun the audio thread. This smoke checks visuals.
	arena.sfx.queue_free()
	arena.sfx = null
	await _ticks(60)
	var first: Fighter = arena.p1
	var second: Fighter = arena.p2
	if args.has("--sprites") or slice:
		var kfm := KfmFrames.get_frames()
		if not _require(first.sprite.visible and first.sprite.sprite_frames != kfm
				and (second.sprite.sprite_frames == kfm) == slice, "Fallback o sets de sprites incorrectos"):
			return
	else:
		if not _require(arena.fighter_views != null, "Los modelos 3D no cargaron"):
			return
		for view: Fighter3DView in arena.fighter_views.models:
			views[view.fighter] = view
			if not _require(not view.fighter.sprite.visible and
					signf(view.transform.basis.x.x) == float(view.fighter.facing()), "Facing o doble render 3D"):
				return
	await _capture("idle")
	Input.action_press("toggle_debug")
	await _ticks(1)
	Input.action_release("toggle_debug")
	if not _require(cfg.show_boxes, "No se activó el overlay de cajas"):
		return
	await _capture("cajas")
	if cpu:
		var exchanged := false
		for tick in (6200 if round_test else 420):
			if tick % 28 == 0:
				Input.action_press("p1_lp")
			elif tick % 28 == 1:
				Input.action_release("p1_lp")
			await physics_frame
			if not exchanged and min(first.health, second.health) < first.max_health:
				exchanged = true
				await _capture("cpu-contacto")
			if arena.match_state.phase == MatchState.ROUND_END:
				await _capture("cpu-fin-round")
				print("Ronda completada vs CPU. Vida P1=%d P2=%d, ganador=%d" %
					[first.health, second.health, arena.match_state.last_winner])
				break
		if not _require(exchanged, "No hubo intercambio de golpes contra CPU"):
			return
		if not _require(not round_test or arena.match_state.phase == MatchState.ROUND_END,
				"No finalizó la ronda contra CPU"):
			return
	else:
		var start_x := first.position.x
		Input.action_press("p1_right")
		await _ticks(12)
		Input.action_release("p1_right")
		if not _require(_clip(first) == &"walk_fwd" and first.position.x > start_x + 20.0,
				"P1 no caminó con su animación"):
			return
		if not await _approach(arena, ["p1_right", "p2_left"]):
			return
		if not await _jab(first, second, "p1_lp", "jab"):
			return
		await _ticks(35)
		# The first hit applies pushback. Close the distance again before P2 attacks.
		if not await _approach(arena, ["p2_left"]):
			return
		if not await _jab(second, first, "p2_lp", "reaccion"):
			return
		if args.has("--match") and not await _play_match(arena):
			return
	if args.has("--throws") and not await _capture_throws(arena):
		return
	if args.has("--ko") and not await _capture_kos(arena):
		return
	if args.has("--arms") and not await _capture_arms(arena):
		return
	print("OK: %s / %s | %s" % [first.character_id, second.character_id, "CPU" if cpu else "dos jugadores"])
	arena.queue_free()
	await process_frame
	await process_frame
	quit()

func _approach(arena: Node, actions: Array[String]) -> bool:
	for action in actions:
		Input.action_press(action)
	for tick in 55:
		if arena.p2.position.x - arena.p1.position.x <= arena.pushbox_min_sep + 1.0:
			break
		await physics_frame
	for action in actions:
		Input.action_release(action)
	await _ticks(3)
	return _require(arena.p2.position.x - arena.p1.position.x <= arena.pushbox_min_sep + 3.0,
		"Los luchadores no se acercaron al rango del jab")

func _jab(attacker: Fighter, defender: Fighter, action: String, screenshot: String) -> bool:
	var hp := defender.health
	var showed_active := false
	var native_art := attacker.sprite.sprite_frames != KfmFrames.get_frames()
	Input.action_press(action)
	await _ticks(1)
	Input.action_release(action)
	for tick in 20:
		await create_timer(0.0).timeout
		if not showed_active and attacker.is_attack_active() and _clip(attacker) == &"stand_lp":
			showed_active = true
			await _capture(screenshot + "-activo")
			if not _require(views.has(attacker) or not native_art or
					(attacker.sprite.frame == 1 and not attacker.sprite.is_playing()),
					"El jab activo no coincide con la pose de impacto"):
				return false
		if showed_active and defender.health == hp - 30 and _clip(defender) == &"hurt":
			await _capture(screenshot + "-dano")
			if native_art:
				if not _require(attacker.hitstop_frames > 3, "No se observó el hitstop"):
					return false
				var saved_tick := _visual_tick(attacker)
				await _ticks(1)
				if not _require(is_equal_approx(_visual_tick(attacker), saved_tick), "La pose avanzó durante el hitstop"):
					return false
			return true
	return _require(false,
		"Jab y reacción inesperados: vida %d -> %d, pose %s" % [hp, defender.health, _clip(defender)])

func _clip(fighter: Fighter) -> StringName:
	return views[fighter].clip if views.has(fighter) else fighter.sprite.animation

func _visual_tick(fighter: Fighter) -> float:
	return views[fighter].sampled_tick if views.has(fighter) else float(fighter.sprite.frame)

func _capture_throws(arena: Node) -> bool:
	root.get_node("GameConfig").show_boxes = false
	for side in 2:
		arena.match_state.reset_match()
		arena._reset_round()
		var attacker: Fighter = arena.p1 if side == 0 else arena.p2
		var defender: Fighter = arena.p2 if side == 0 else arena.p1
		var facing := 1 if side == 0 else -1
		attacker.position.x = arena.stage_left + 4.0 if side == 0 else arena.stage_right - 4.0
		defender.position.x = attacker.position.x + facing * 46.0
		await _ticks(60)
		var prefix := attacker.character_id + "-agarre-"
		var first_key := KEY_U if side == 0 else KEY_N
		var second_key := KEY_J if side == 0 else KEY_COMMA
		_key(first_key, true)
		await _ticks(2)
		_key(second_key, true)
		await _ticks(2)
		_key(first_key, false)
		_key(second_key, false)
		for checkpoint in [&"grabbed_hold", &"thrown_air", &"down_hold", &"getup", &"idle"]:
			var found := false
			for tick in 65:
				await create_timer(0.0).timeout
				if _clip(defender) == checkpoint:
					if checkpoint == &"grabbed_hold" and _visual_tick(defender) < 9.0:
						continue
					if checkpoint in [&"thrown_air", &"getup"] and _visual_tick(defender) < 6.0:
						continue
					found = true
					await _capture(prefix + checkpoint)
					break
			if not _require(found, "No se observó " + checkpoint + " para " + attacker.character_id):
				return false
	return true

func _capture_kos(arena: Node) -> bool:
	root.get_node("GameConfig").show_boxes = false
	for side in 2:
		arena.match_state.reset_match()
		arena._reset_round()
		var attacker: Fighter = arena.p1 if side == 0 else arena.p2
		var defender := attacker.opponent
		attacker.position.x = 160.0 if side == 0 else 208.0
		defender.position.x = 208.0 if side == 0 else 160.0
		await _ticks(60)
		defender.health = 30
		var key := KEY_U if side == 0 else KEY_COMMA
		_key(key, true)
		await _ticks(1)
		_key(key, false)
		for tick in 25:
			await create_timer(0.0).timeout
			if _clip(defender) == &"ko_fall" and _visual_tick(defender) >= 6.0:
				await _capture(defender.character_id + "-ko-caida")
				break
		await _ticks(30)
		if not _require(defender.health == 0 and _clip(defender) == &"down_hold",
				"KO sin pose final para " + defender.character_id):
			return false
		await _capture(defender.character_id + "-ko-suelo")
	return true

func _key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)
	Input.flush_buffered_events()

func _capture_arms(arena: Node) -> bool:
	root.get_node("GameConfig").show_boxes = false
	for side in 2:
		arena.match_state.reset_match()
		arena._reset_round()
		var attacker: Fighter = arena.p1 if side == 0 else arena.p2
		var defender := attacker.opponent
		arena.p1.position.x = 150.0
		arena.p2.position.x = 222.0
		await _ticks(60)
		var action := "p1_hp" if side == 0 else "p2_hp"
		var life := defender.health
		await _capture(attacker.character_id + "-brazo-000")
		Input.action_press(action)
		for tick in range(1, 49):
			await physics_frame
			await _capture(attacker.character_id + "-brazo-%03d" % tick)
			if tick == 1:
				Input.action_release(action)
		if not _require(defender.health < life and _clip(attacker) == &"idle",
				"Golpe fuerte sin impacto o recuperación: " + attacker.character_id):
			return false
	return true

func _play_match(arena: Node) -> bool:
	for tick in 3500:
		if arena.p2.position.x - arena.p1.position.x > 45.0:
			Input.action_press("p1_right")
		else:
			Input.action_release("p1_right")
		if tick % 28 == 0:
			Input.action_press("p1_lp")
		elif tick % 28 == 1:
			Input.action_release("p1_lp")
		await physics_frame
		if arena.match_state.match_over():
			break
	Input.action_release("p1_lp")
	Input.action_release("p1_right")
	await _capture("fin-match")
	print("Resultado local: rounds P1=%d P2=%d" % [arena.match_state.p1_rounds, arena.match_state.p2_rounds])
	return _require(arena.match_state.match_winner() == 1, "El combate local no terminó con victoria de P1")

func _ticks(count: int) -> void:
	for tick in count:
		await physics_frame
	await process_frame

func _capture(name: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	var path := output.path_join(name + ".png")
	if root.get_texture().get_image().save_png(path) != OK:
		printerr("Error al guardar ", path)
		quit(1)

func _require(condition: bool, message: String) -> bool:
	if not condition:
		printerr(message)
		quit(1)
	return condition
