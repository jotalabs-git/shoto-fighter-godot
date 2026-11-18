class_name Throws
extends RefCounted

## Resolución de agarres entre dos fighters. Si ambos intentan agarrar en rango el mismo
## frame -> throw tech (se separan, sin daño). Si solo uno -> agarra (knockdown al rival).
static func resolve(a: Fighter, b: Fighter, throw_range: float) -> void:
	var dist: float = absf(a.position.x - b.position.x)
	if dist > throw_range:
		return
	# Un botón liviano puede haber iniciado su arranque antes de resolver el acorde.
	if a.throw_pressed and b.throw_pressed:
		a.throw_tech()
		b.throw_tech()
	elif a.throw_pressed and b.is_throwable():
		a.do_throw(b)
	elif b.throw_pressed and a.is_throwable():
		b.do_throw(a)
