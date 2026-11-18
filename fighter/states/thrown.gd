extends State

## Fase de sujeción de un agarre exitoso.
## El atacante controla el instante del lanzamiento; mientras tanto,
## la víctima permanece junto a él y no puede ejecutar acciones.
func enter() -> void:
	fighter.vel = Vector2.ZERO

func physics_update(_delta: float) -> void:
	fighter.vel = Vector2.ZERO
