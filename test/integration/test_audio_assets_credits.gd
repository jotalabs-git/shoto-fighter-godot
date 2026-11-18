extends GdUnitTestSuite

const MENU := preload("res://ui/main_menu.tscn")
const CREDITS := preload("res://ui/credits.tscn")

func test_kenney_cc0_audio_files_are_bundled() -> void:
	for filename in [
		"hit_punch_light", "hit_punch_medium", "hit_punch_heavy",
		"hit_kick_light", "hit_kick_medium", "hit_kick_heavy",
		"hit_sweep", "block", "grab", "fall", "hit_energy",
		"announcer_round_1", "announcer_round_2", "announcer_round_3",
		"announcer_fight", "announcer_winner", "announcer_game_over",
	]:
		assert_bool(ResourceLoader.exists("res://assets/audio/" + filename + ".ogg")).is_true()

func test_credit_scene_lists_mandatory_bart_attribution() -> void:
	var credits := CREDITS.instantiate()
	add_child(credits)
	auto_free(credits)
	var scroll := credits.get_child(2) as ScrollContainer
	assert_bool(scroll != null).is_true()
	var text_content := scroll.get_child(0) as RichTextLabel
	assert_str(text_content.text).contains("bart")
	assert_str(text_content.text).contains("CC BY 3.0")
	assert_str(text_content.text).contains("opengameart.org")

func test_menu_offers_credits_and_voice_selection() -> void:
	var menu := MENU.instantiate()
	add_child(menu)
	auto_free(menu)
	assert_object(menu.get_node("BtnCredits")).is_not_null()
	assert_object(menu.get_node("BtnVoices")).is_not_null()
