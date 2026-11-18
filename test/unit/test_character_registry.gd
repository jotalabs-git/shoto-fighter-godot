extends GdUnitTestSuite

func test_prototype_names_are_registered() -> void:
	assert_str(CharacterRegistry.display_name("guitarist")).is_equal("EL GUITARRISTA")
	assert_str(CharacterRegistry.display_name("frontman")).is_equal("EL FRONTMAN")

func test_prototypes_keep_distinct_combat_profiles() -> void:
	assert_float(Characters.stats("frontman")["walk_fwd_speed"]).is_greater(Characters.stats("guitarist")["walk_fwd_speed"])
	assert_int(Characters.specials_for("frontman")["dp.l"].damage).is_greater(Characters.specials_for("guitarist")["dp.l"].damage)

func test_unfinished_art_falls_back_to_kung_fu_man() -> void:
	assert_bool(CharacterFrames.has_custom_art("kaze")).is_false()
	assert_object(CharacterFrames.get_frames("kaze")).is_same(KfmFrames.get_frames())
	assert_vector(CharacterFrames.get_axis("kaze")).is_equal(KfmFrames.axis)

func test_guitarist_loads_original_sprites() -> void:
	var frames := CharacterFrames.get_frames("guitarist")
	assert_bool(CharacterFrames.has_custom_art("guitarist")).is_true()
	assert_bool(frames != KfmFrames.get_frames()).is_true()
	assert_bool(frames.has_animation("stand_lp")).is_true()
	assert_str(frames.get_frame_texture("idle", 0).resource_path).contains("/guitarist/idle/")
	assert_vector(CharacterFrames.get_axis("guitarist")).is_equal(Vector2(79, 136))

func test_frontman_loads_an_independent_sprite_set() -> void:
	var frames := CharacterFrames.get_frames("frontman")
	assert_bool(CharacterFrames.has_custom_art("frontman")).is_true()
	assert_bool(frames != KfmFrames.get_frames()).is_true()
	assert_bool(frames != CharacterFrames.get_frames("guitarist")).is_true()
	assert_str(frames.get_frame_texture("idle", 0).resource_path).contains("/frontman/idle/")
	assert_vector(CharacterFrames.get_axis("frontman")).is_equal(Vector2(79, 136))
