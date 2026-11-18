# Regression: el audio debe poder inicializar sin bloquear MatchManager
# y los dos luchadores deben mirar uno hacia el otro sin invertir las hitboxes.
extends GdUnitTestSuite

const MATCH := preload("res://match/match.tscn")

func _match() -> MatchManager:
	var match: MatchManager = MATCH.instantiate()
	add_child(match)
	auto_free(match)
	return match

func test_match_initializes_audio_and_character_orientations() -> void:
	var match := _match()
	var guitarist: Fighter = match.p1
	var frontman: Fighter = match.p2

	assert_object(match.sfx).is_not_null()
	assert_bool(match.sfx._bank.has("hit_punch_light")).is_true()
	assert_int(guitarist.facing()).is_equal(1)
	assert_int(frontman.facing()).is_equal(-1)
	assert_int(CharacterRegistry.art_facing("guitarist")).is_equal(1)
	assert_int(CharacterRegistry.art_facing("frontman")).is_equal(-1)

	guitarist._process(0.0)
	frontman._process(0.0)
	# Ambos sprites conservan su orientación de autor; el del cantante
	# se compensa en la presentación para verse de frente al guitarrista.
	assert_float(guitarist.sprite.scale.x).is_equal_approx(0.85, 0.001)
	assert_float(frontman.sprite.scale.x).is_equal_approx(0.85, 0.001)

func test_match_connects_a_punch_after_loading_sfx() -> void:
	var match := _match()
	var guitarist: Fighter = match.p1
	var frontman: Fighter = match.p2
	guitarist.position.x = 140.0
	frontman.position.x = 184.0
	guitarist.start_move(guitarist.moves["st.lp"])
	guitarist.state_machine.transition_to("Attack")

	for i in 16:
		await get_tree().physics_frame
	assert_int(frontman.health).is_less(frontman.max_health)
	assert_bool(guitarist.move_has_hit).is_true()
