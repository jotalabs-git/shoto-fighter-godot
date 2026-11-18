extends GdUnitTestSuite

const SELECT := preload("res://ui/character_select.tscn")
const MATCH := preload("res://match/match.tscn")

func after_test() -> void:
	GameConfig.p1_character_id = "guitarist"
	GameConfig.p2_character_id = "frontman"
	GameConfig.p2_is_cpu = false

func test_four_characters_have_models_and_idle_clips() -> void:
	assert_int(CharacterRegistry.selectable_ids().size()).is_equal(4)
	for id: String in CharacterRegistry.selectable_ids():
		var path := CharacterRegistry.model_path(id)
		assert_bool(ResourceLoader.exists(path)).is_true()
		var scene := load(path) as PackedScene
		assert_bool(scene != null).is_true()
		if scene == null:
			continue
		var model := scene.instantiate() as Node3D
		assert_bool(model != null).is_true()
		if model == null:
			continue
		auto_free(model)
		var animators := model.find_children("*", "AnimationPlayer", true, false)
		assert_bool(not animators.is_empty()).is_true()
		if not animators.is_empty():
			assert_bool((animators[0] as AnimationPlayer).has_animation("idle")).is_true()

func test_selection_shows_two_standing_3d_previews() -> void:
	GameConfig.p2_is_cpu = false
	var select := SELECT.instantiate()
	add_child(select)
	auto_free(select)
	assert_int(select._cards.size()).is_equal(4)
	assert_int(select._viewport_nodes.size()).is_equal(2)
	assert_bool(is_instance_valid(select._models[0])).is_true()
	assert_bool(is_instance_valid(select._models[1])).is_true()
	assert_str(select._names[0].text).contains("GUITARRISTA")
	assert_str(select._names[1].text).contains("FRONTMAN")

func test_both_local_players_change_previews_independently() -> void:
	GameConfig.p2_is_cpu = false
	var select := SELECT.instantiate()
	add_child(select)
	auto_free(select)
	select._move_selection(0, 2)
	assert_str(select._names[0].text).contains("OZZY")
	assert_str(select._names[1].text).contains("FRONTMAN")
	select._move_selection(1, 3)
	assert_str(select._names[1].text).contains("BRUCE")
	assert_str(select._names[0].text).contains("OZZY")
	assert_bool(is_instance_valid(select._models[0])).is_true()
	assert_bool(is_instance_valid(select._models[1])).is_true()

func test_preview_cameras_face_the_models_and_use_brand_fonts() -> void:
	GameConfig.p2_is_cpu = false
	var select := SELECT.instantiate()
	add_child(select)
	auto_free(select)
	for side in 2:
		var camera := select._viewport_nodes[side].get_node("PreviewCamera") as Camera3D
		assert_bool(camera.is_inside_tree()).is_true()
		var direction := (Vector3(0.0, 1.27, 0.0) - camera.global_position).normalized()
		assert_float((-camera.global_basis.z).dot(direction)).is_greater(0.99)
	for card: Button in select._cards:
		assert_bool(card.get_theme_font("font") != null).is_true()

func test_character_configuration_is_applied_on_match_enter_tree() -> void:
	GameConfig.set_characters("ozzy", "bruce")
	var arena: MatchManager = MATCH.instantiate()
	add_child(arena)
	auto_free(arena)
	assert_str(arena.p1.character_id).is_equal("ozzy")
	assert_str(arena.p2.character_id).is_equal("bruce")
	assert_str(CharacterRegistry.display_name("ozzy")).contains("OZZY")
	assert_str(CharacterRegistry.display_name("bruce")).contains("BRUCE")

func test_cpu_opponent_is_distinct_when_randomized() -> void:
	GameConfig.p2_is_cpu = true
	var select := SELECT.instantiate()
	add_child(select)
	auto_free(select)
	assert_int(select._indices[0]).is_not_equal(select._indices[1])
	assert_bool(select._confirmed[1]).is_true()
