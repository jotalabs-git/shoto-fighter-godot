extends GdUnitTestSuite

const MATCH := preload("res://match/match.tscn")

func _arena(second_id := "frontman", mode := "3d") -> MatchManager:
	var arena: MatchManager = MATCH.instantiate()
	arena.presentation_mode = mode
	arena.get_node("Player2").character_id = second_id
	add_child(arena)
	auto_free(arena)
	arena.set_physics_process(false)
	for fighter in [arena.p1, arena.p2]:
		fighter.set_physics_process(false)
	return arena

func _tick(fighter: Fighter, count: int) -> void:
	for i in count:
		fighter.state_machine.physics_update(1.0 / 60.0)

func _place(arena: MatchManager, attacker: Fighter, defender: Fighter, facing: int) -> void:
	attacker.position.x = arena.stage_left + 3.0 if facing == 1 else arena.stage_right - 3.0
	defender.position.x = attacker.position.x + facing * 47.0
	attacker._update_facing()
	defender._update_facing()
	arena.fighter_views._process(0.0)

func test_both_imports_have_distinct_clips_and_canonical_facing() -> void:
	var arena := _arena()
	assert_object(arena.fighter_views).is_not_null()
	var renderer := arena.fighter_views
	for view in renderer.models:
		assert_int(view.clips.size()).is_equal(47)
		assert_int(view.skeleton.get_bone_count()).is_equal(15)
		assert_bool(view.fighter.sprite.visible).is_false()
		for clip: String in view.clips:
			var animation := view.player.get_animation(clip)
			assert_float(animation.length).is_greater(0.0)
			assert_int(animation.get_track_count()).is_greater(0)
		var rest := view.skeleton.get_bone_global_pose(view.skeleton.find_bone("fist_near"))
		view.sample(&"jump_lp", 4)
		assert_bool(view.skeleton.get_bone_global_pose(view.skeleton.find_bone("fist_near")) != rest).is_true()
	_place(arena, arena.p1, arena.p2, -1)
	assert_float(renderer.models[0].transform.basis.x.x).is_less(0.0)
	assert_float(renderer.models[1].transform.basis.x.x).is_greater(0.0)

func test_guest_musicians_use_the_combat_rig_and_clips() -> void:
	for id: String in ["ozzy", "bruce"]:
		var arena := _arena(id)
		assert_object(arena.fighter_views).is_not_null()
		if arena.fighter_views == null:
			return
		var model := arena.fighter_views.models[1]
		assert_int(model.clips.size()).is_equal(47)
		assert_int(model.skeleton.get_bone_count()).is_equal(15)
		assert_bool(arena.p2.sprite.visible).is_false()
		model.sample(&"idle", 0)
		var guard := model._bone_point("fist_near")
		model.sample(&"stand_hp", model.clips["stand_hp"]["impact"])
		assert_float(model._bone_point("fist_near").distance_to(guard)).is_greater(0.4)

func test_arm_lengths_stay_fixed_through_walk_and_punches() -> void:
	var arena := _arena()
	for view: Fighter3DView in arena.fighter_views.models:
		for clip: StringName in [&"walk_fwd", &"stand_hp", &"crouch_mp", &"jump_mp", &"upper"]:
			for tick in range(0, int(view.clips[clip]["ticks"]), 2):
				view.sample(clip, tick)
				for side in ["near", "far"]:
					var shoulder := view._bone_point("bicep_" + side)
					var elbow := view._bone_point("forearm_" + side)
					var wrist := view._bone_point("fist_" + side)
					assert_float(shoulder.distance_to(elbow)).is_equal_approx(0.43, 0.003)
					assert_float(elbow.distance_to(wrist)).is_equal_approx(0.44, 0.003)
		view.sample(&"stand_lp", 0)
		var guard := view._bone_point("fist_near") - view._bone_point("head")
		view.sample(&"stand_lp", view.clips["stand_lp"]["impact"])
		assert_float(view._bone_point("fist_near").x * view.fighter.facing()).is_greater(
			view._bone_point("bicep_near").x * view.fighter.facing() + 0.6)
		assert_vector(view._bone_point("fist_near") - view._bone_point("head")).is_not_equal(guard)

func test_grips_at_both_walls_release_hold_getup_and_clear() -> void:
	var arena := _arena()
	# Each musician throws in both orientations, with the 2D root checked independently.
	for attacker: Fighter in [arena.p1, arena.p2]:
		var defender := attacker.opponent
		var index := attacker.team
		var victim_view := arena.fighter_views.models[1 - index]
		var attack_view := arena.fighter_views.models[index]
		for direction in [-1, 1]:
			arena._reset_round()
			_place(arena, attacker, defender, direction)
			var initial := defender.global_position
			attacker.do_throw(defender)
			_tick(attacker, 10)
			arena.fighter_views._process(0.0)
			assert_str(victim_view.clip).is_equal("grabbed_hold")
			assert_float(victim_view.sampled_tick).is_equal(10.0)
			assert_vector(defender.global_position).is_equal(initial)
			assert_int(defender.health).is_equal(defender.max_health)
			assert_float(victim_view.grip_offset.length()).is_greater(0.02)
			var hands := (attack_view._bone_point("fist_near") + attack_view._bone_point("fist_far")) * 0.5
			var chest := victim_view._bone_point("pelvis", Vector3(0, 0.49, 0))
			assert_float(hands.distance_to(chest)).is_less(0.46)
			_tick(attacker, 1)
			assert_int(defender.health).is_equal(defender.max_health)
			_tick(attacker, 1)
			arena.fighter_views._process(0.0)
			assert_str(victim_view.clip).is_equal("thrown_air")
			assert_int(defender.health).is_equal(defender.max_health - Fighter.THROW_DAMAGE)
			_tick(attacker, 8)
			assert_str(attacker.state_machine.current_state.name).is_equal("Idle")
			_tick(defender, 13)
			arena.fighter_views._process(0.0)
			assert_str(victim_view.clip).is_equal("down_hold")
			assert_float(victim_view.grip_offset.length()).is_equal(0.0)
			_tick(defender, 14)
			arena.fighter_views._process(0.0)
			assert_str(victim_view.clip).is_equal("down_hold")
			_tick(defender, 1)
			arena.fighter_views._process(0.0)
			assert_str(victim_view.clip).is_equal("getup")
			_tick(defender, 12)
			arena.fighter_views._process(0.0)
			assert_str(victim_view.clip).is_equal("idle")
			assert_int(defender.health).is_equal(defender.max_health - Fighter.THROW_DAMAGE)

func test_ko_stays_down_and_failed_or_teched_grips_do_not_zoom() -> void:
	var arena := _arena()
	var attacker := arena.p1
	var defender := arena.p2
	attacker.throw_pressed = true
	arena._physics_process(1.0 / 60.0)
	assert_int(arena._throw_closeup_remaining).is_equal(0)
	_place(arena, attacker, defender, 1)
	defender.throw_pressed = true
	arena._physics_process(1.0 / 60.0)
	assert_int(arena._throw_closeup_remaining).is_equal(0)
	attacker.throw_pressed = false
	defender.throw_pressed = false

	defender.health = Fighter.THROW_DAMAGE
	attacker.do_throw(defender)
	_tick(attacker, 12)
	arena._physics_process(1.0 / 60.0)
	for i in 55:
		defender._physics_process(1.0 / 60.0)
	arena.fighter_views._process(0.0)
	assert_int(defender.health).is_equal(0)
	assert_str(defender.state_machine.current_state.name).is_equal("Knockdown")
	assert_str(arena.fighter_views.models[1].clip).is_equal("down_hold")
	arena._reset_round()
	arena.fighter_views._process(0.0)
	assert_str(arena.fighter_views.models[1].clip).is_equal("idle")

func test_explicit_and_missing_model_fallback() -> void:
	var explicit := _arena("frontman", "sprites")
	assert_bool(explicit.fighter_views == null).is_true()
	assert_bool(explicit.p1.sprite.visible).is_true()
	var missing := _arena("homura")
	assert_bool(missing.fighter_views == null).is_true()
	assert_bool(missing.p1.sprite.visible and missing.p2.sprite.visible).is_true()

func test_sweep_and_plain_ko_have_their_own_fall_and_contact() -> void:
	var arena := _arena()
	var victim := arena.p2
	var view := arena.fighter_views.models[1]
	var contacts: Array[String] = []
	victim.fall_cued.connect(func(character: String) -> void: contacts.append(character))
	victim.receive_hit(arena.p1.moves["cr.hk"], 1)
	arena.fighter_views._process(0.0)
	assert_str(view.clip).is_equal("knockdown_low")
	_tick(victim, 9)
	assert_int(contacts.size()).is_equal(0)
	_tick(victim, 1)
	assert_int(contacts.size()).is_equal(1)
	arena.fighter_views._process(0.0)
	assert_float(view.sampled_tick).is_equal(float(view.clips["knockdown_low"]["ground_contact"]))
	_tick(victim, 5)
	arena.fighter_views._process(0.0)
	assert_str(view.clip).is_equal("down_hold")
	arena._reset_round()
	victim.health = 1
	victim.receive_hit(arena.p1.moves["st.hp"], 1)
	arena.fighter_views._process(0.0)
	assert_str(view.clip).is_equal("ko_fall")
	arena._physics_process(1.0 / 60.0)
	for i in 55:
		victim._physics_process(1.0 / 60.0)
	arena.fighter_views._process(0.0)
	assert_str(view.clip).is_equal("down_hold")
	assert_int(contacts.size()).is_equal(2)
