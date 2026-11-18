extends GdUnitTestSuite

func test_light_medium_and_heavy_hits_have_distinct_sound_keys() -> void:
	var normal := MoveSet.default_normals()
	assert_str(SoundProfile.impact_key(normal["st.lp"])).is_equal("hit_punch_light")
	assert_str(SoundProfile.impact_key(normal["st.mp"])).is_equal("hit_punch_medium")
	assert_str(SoundProfile.impact_key(normal["st.hp"])).is_equal("hit_punch_heavy")
	assert_str(SoundProfile.impact_key(normal["st.hk"])).is_equal("hit_kick_heavy")
	assert_str(SoundProfile.impact_key(normal["cr.hk"])).is_equal("hit_sweep")

func test_block_and_projectile_use_unique_sounds() -> void:
	var normal := MoveSet.default_normals()
	var specials := MoveSet.default_specials()
	assert_str(SoundProfile.impact_key(normal["st.hp"], true)).is_equal("block")
	assert_str(SoundProfile.impact_key(specials["hadouken.l"])).is_equal("hit_energy")

func test_fighter_sound_banks_are_independent() -> void:
	assert_str(SoundProfile.fighter_voice("guitarist")).is_equal("guitarist")
	assert_str(SoundProfile.fighter_voice("frontman")).is_equal("frontman")
	assert_str(SoundProfile.fighter_voice("kaze")).is_equal("neutral")

func test_generated_combat_samples_exist_and_are_nonempty() -> void:
	var sound := Sfx.new()
	add_child(sound)
	auto_free(sound)
	for key in ["hit_punch_light", "hit_punch_medium", "hit_kick_heavy", "block", "fall", "grab", "ko", "voice_guitarist_effort_heavy", "voice_frontman_hurt"]:
		var stream: AudioStream = sound._bank.get(key)
		assert_bool(stream != null).is_true()
		assert_float(stream.get_length()).is_greater(0.0)
