extends State

## Los últimos doce ticks del derribo se reservan para levantarse.
var _played_contact := false

func enter() -> void:
	_played_contact = false

func physics_update(delta: float) -> void:
	if not fighter.on_ground:
		fighter.apply_gravity(delta)
	fighter.vel.x = move_toward(fighter.vel.x, 0.0, 800.0 * delta)
	fighter.knockdown_frames -= 1
	if fighter.on_ground and fighter.health > 0:
		if not _played_contact and state_frame >= fighter.fall_contact_tick():
			_played_contact = true
			fighter.fall_cued.emit(fighter.character_id)
		if fighter.knockdown_frames <= Fighter.GETUP_FRAMES:
			state_machine.transition_to("Getup")
