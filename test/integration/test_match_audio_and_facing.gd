# Regression: el audio debe poder inicializar sin bloquear MatchManager
# y los dos luchadores deben mirar uno hacia el otro sin invertir las hitboxes.
extends GdUnitTestSuite

const MATCH := preload("res://match/match.tscn")

func _match() -> MatchManager:
	var arena: MatchManager = MATCH.instantiate()
	arena.presentation_mode = "sprites"
	add_child(arena)
	auto_free(arena)
	return arena

func test_match_initializes_audio_and_character_orientations() -> void:
	var arena := _match()
	var guitarist: Fighter = arena.p1
	var frontman: Fighter = arena.p2

	assert_object(arena.sfx).is_not_null()
	assert_bool(arena.sfx._bank.has("hit_punch_light")).is_true()
	assert_int(guitarist.facing()).is_equal(1)
	assert_int(frontman.facing()).is_equal(-1)
	assert_int(CharacterRegistry.art_facing("guitarist")).is_equal(1)
	assert_int(CharacterRegistry.art_facing("frontman")).is_equal(-1)

	guitarist._process(0.0)
	frontman._process(0.0)
	for fighter: Fighter in [guitarist, frontman]:
		var sprite := fighter.sprite
		var facing := fighter.facing() * CharacterRegistry.art_facing(fighter.character_id)
		var frame := sprite.sprite_frames.get_frame_texture("idle", 0)
		assert_bool(sprite.texture_filter == CanvasItem.TEXTURE_FILTER_LINEAR).is_true()
		assert_vector(frame.get_size()).is_equal(Vector2(528, 444))
		assert_float(sprite.scale.x * 3.0).is_equal_approx(0.85 * facing, 0.001)
		assert_float(sprite.scale.y * 3.0).is_equal_approx(0.85, 0.001)
		assert_vector(sprite.offset).is_equal(-CharacterFrames.get_axis(fighter.character_id) * 3.0)

func test_match_connects_a_punch_after_loading_sfx() -> void:
	var arena := _match()
	var guitarist: Fighter = arena.p1
	var frontman: Fighter = arena.p2
	guitarist.position.x = 140.0
	frontman.position.x = 184.0
	guitarist.start_move(guitarist.moves["st.lp"])
	guitarist.state_machine.transition_to("Attack")

	for i in 16:
		await get_tree().physics_frame
	assert_int(frontman.health).is_less(frontman.max_health)
	assert_bool(guitarist.move_has_hit).is_true()
