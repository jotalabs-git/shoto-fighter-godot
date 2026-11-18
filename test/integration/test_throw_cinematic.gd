# Integración: agarre sincronizado sin cambiar daño ni permitir doble impacto.
extends GdUnitTestSuite

const FIGHTER := preload("res://fighter/fighter.tscn")

func _fighters() -> Array:
	var a: Fighter = FIGHTER.instantiate()
	var b: Fighter = FIGHTER.instantiate()
	a.position = Vector2(160.0, 180.0)
	b.position = Vector2(210.0, 180.0)
	a.facing_right = true
	b.facing_right = false
	add_child(a)
	add_child(b)
	auto_free(a)
	auto_free(b)
	return [a, b]

func test_throw_holds_victim_before_impact_then_applies_damage_once() -> void:
	var fighters := _fighters()
	var attacker: Fighter = fighters[0]
	var victim: Fighter = fighters[1]
	attacker.do_throw(victim)
	assert_str(attacker.state_machine.current_state.name).is_equal("Throw")
	assert_str(victim.state_machine.current_state.name).is_equal("Thrown")
	assert_int(victim.health).is_equal(victim.max_health)
	for i in range(11):
		attacker.state_machine.physics_update(1.0 / 60.0)
	assert_str(victim.state_machine.current_state.name).is_equal("Thrown")
	assert_int(victim.health).is_equal(victim.max_health)
	attacker.state_machine.physics_update(1.0 / 60.0)
	assert_str(victim.state_machine.current_state.name).is_equal("Knockdown")
	assert_int(victim.health).is_equal(victim.max_health - Fighter.THROW_DAMAGE)
	attacker.release_throw_victim()
	assert_int(victim.health).is_equal(victim.max_health - Fighter.THROW_DAMAGE)

func test_throw_interruption_releases_victim() -> void:
	var fighters := _fighters()
	var attacker: Fighter = fighters[0]
	var victim: Fighter = fighters[1]
	attacker.do_throw(victim)
	attacker.state_machine.transition_to("Idle")
	assert_str(victim.state_machine.current_state.name).is_equal("Knockdown")
	assert_int(victim.health).is_equal(victim.max_health - Fighter.THROW_DAMAGE)

func test_throw_works_when_second_fighter_attacks() -> void:
	var fighters := _fighters()
	var attacker: Fighter = fighters[1]
	var victim: Fighter = fighters[0]
	attacker.do_throw(victim)
	for i in range(12):
		attacker.state_machine.physics_update(1.0 / 60.0)
	assert_str(victim.state_machine.current_state.name).is_equal("Knockdown")
	assert_float(victim.vel.x).is_less(0.0)
	assert_int(victim.health).is_equal(victim.max_health - Fighter.THROW_DAMAGE)
