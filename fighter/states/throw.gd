extends State

## Agarre cinemático: la víctima permanece sujeta hasta el impacto.
## 12 ticks de anticipación y lanzamiento, 8 ticks de recuperación.
const RELEASE_FRAME := 12
const TOTAL_FRAMES := 20

func enter() -> void:
	fighter.stop_horizontal()

func physics_update(_delta: float) -> void:
	if state_frame >= RELEASE_FRAME:
		fighter.release_throw_victim()
	if state_frame >= TOTAL_FRAMES:
		state_machine.transition_to("Idle")

func exit() -> void:
	# Evita dejar al rival inmovilizado si el atacante es interrumpido.
	fighter.cancel_throw_victim()
