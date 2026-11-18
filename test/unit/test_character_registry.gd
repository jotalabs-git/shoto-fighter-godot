extends GdUnitTestSuite

func test_prototype_names_are_registered() -> void:
	assert_str(CharacterRegistry.display_name("guitarist")).is_equal("EL GUITARRISTA")
	assert_str(CharacterRegistry.display_name("frontman")).is_equal("EL FRONTMAN")

func test_prototypes_keep_distinct_combat_profiles() -> void:
	assert_float(Characters.stats("frontman")["walk_fwd_speed"]).is_greater(Characters.stats("guitarist")["walk_fwd_speed"])
	assert_int(Characters.specials_for("frontman")["dp.l"].damage).is_greater(Characters.specials_for("guitarist")["dp.l"].damage)

func test_unfinished_art_falls_back_to_kung_fu_man() -> void:
	assert_bool(CharacterFrames.has_custom_art("guitarist")).is_false()
	assert_bool(CharacterFrames.has_custom_art("frontman")).is_false()
	assert_object(CharacterFrames.get_frames("guitarist")).is_same(CharacterFrames.get_frames("frontman"))
	assert_vector(CharacterFrames.get_axis("guitarist")).is_equal(KfmFrames.axis)
