extends State

func enter() -> void:
	fighter.stop_horizontal()

func physics_update(_delta: float) -> void:
	if fighter.health <= 0:
		fighter.begin_knockdown(&"normal")
		return
	fighter.knockdown_frames -= 1
	if state_frame >= Fighter.GETUP_FRAMES:
		state_machine.transition_to("Idle")
