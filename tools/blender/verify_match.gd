extends SceneTree
## End-to-end screenshot and combat smoke test using the shipped match and InputMap.

var output: String
var cpu: bool
var slice: bool
var round_test: bool

func _initialize() -> void:
	call_deferred("_verify")

func _verify() -> void:
	var args := OS.get_cmdline_user_args()
	if args.is_empty():
		printerr("Uso: verify_match.gd -- DIRECTORIO [--cpu] [--slice] [--round] [--match]")
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
	var arena: MatchManager = load("res://match/match.tscn").instantiate()
	root.add_child(arena)
	# Fixed simulation steps can outrun the audio thread. This smoke checks visuals.
	arena.sfx.queue_free()
	arena.sfx = null
	await _ticks(60)
	var first := arena.p1
	var second := arena.p2
	var kfm := KfmFrames.get_frames()
	if not _require(first.sprite.sprite_frames != kfm, "P1 cargó sprites KFM"):
		return
	if not _require((second.sprite.sprite_frames == kfm) == slice, "Set visual de P2 incorrecto"):
		return
	if not _require(first.sprite.sprite_frames != second.sprite.sprite_frames
			and second.sprite.scale.x < 0 and first.sprite.scale.x > 0, "Sets o reflejo incorrectos"):
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
		if not _require(first.sprite.animation == "walk_fwd" and first.position.x > start_x + 20.0,
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
	print("OK: %s / %s | %s" % [first.character_id, second.character_id, "CPU" if cpu else "dos jugadores"])
	arena.queue_free()
	await process_frame
	await process_frame
	quit()

func _approach(arena: MatchManager, actions: Array[String]) -> bool:
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
		if not showed_active and attacker.is_attack_active() and attacker.sprite.animation == "stand_lp":
			showed_active = true
			await _capture(screenshot + "-activo")
			if not _require(not native_art or (attacker.sprite.frame == 1 and not attacker.sprite.is_playing()),
					"El jab activo no coincide con la pose de impacto"):
				return false
		if showed_active and defender.health == hp - 30 and defender.sprite.animation == "hurt":
			await _capture(screenshot + "-dano")
			if native_art:
				if not _require(attacker.hitstop_frames > 3, "No se observó el hitstop"):
					return false
				await _ticks(1)
				if not _require(attacker.sprite.frame == 1, "La pose avanzó durante el hitstop"):
					return false
			return true
	return _require(false,
		"Jab y reacción inesperados: vida %d -> %d, pose %s" % [hp, defender.health, defender.sprite.animation])

func _play_match(arena: MatchManager) -> bool:
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
