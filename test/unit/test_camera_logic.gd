# Unit: cálculo de cámara (centro + zoom acotado).
extends GdUnitTestSuite

func test_center_is_midpoint() -> void:
	var c := CameraLogic.compute(100.0, 200.0, 384.0, 0.85, 1.6, 90.0)
	assert_float(c[0]).is_equal(150.0)

func test_zoom_clamped_to_max_when_close() -> void:
	# needed = 10 + 180 = 190; 384/190 ~= 2.02 -> clamp a max 1.6
	var c := CameraLogic.compute(100.0, 110.0, 384.0, 0.85, 1.6, 90.0)
	assert_float(c[1]).is_equal(1.6)

func test_zoom_clamped_to_min_when_far() -> void:
	# needed = 384 + 180 = 564; 384/564 ~= 0.68 -> clamp a min 0.85
	var c := CameraLogic.compute(0.0, 384.0, 384.0, 0.85, 1.6, 90.0)
	assert_float(c[1]).is_equal(0.85)

func test_wider_stage_zoom_out_is_progressive() -> void:
	# Con los parametros actuales del match, la distancia incrementa
	# gradualmente el campo visible, sin cambiar el centro del combate.
	var close := CameraLogic.compute(170.0, 214.0, 384.0, 0.70, 1.20, 85.0)
	var start := CameraLogic.compute(112.0, 272.0, 384.0, 0.70, 1.20, 85.0)
	var far := CameraLogic.compute(-32.0, 416.0, 384.0, 0.70, 1.20, 85.0)
	assert_float(close[1]).is_greater(start[1])
	assert_float(start[1]).is_greater(far[1])
	assert_float(far[1]).is_equal(0.70)
	assert_float(close[0]).is_equal(192.0)
	assert_float(start[0]).is_equal(192.0)
	assert_float(far[0]).is_equal(192.0)

func test_throw_closeup_tracks_both_fighters_without_changing_their_positions() -> void:
	var closeup := CameraLogic.throw_closeup(164.0, 220.0, 1.55)
	assert_float(closeup[0]).is_equal(192.0)
	assert_float(closeup[1]).is_equal(1.55)

func test_throw_closeup_keeps_center_when_attacker_is_on_other_side() -> void:
	var closeup := CameraLogic.throw_closeup(220.0, 164.0, 1.55)
	assert_float(closeup[0]).is_equal(192.0)
	assert_float(closeup[1]).is_equal(1.55)
