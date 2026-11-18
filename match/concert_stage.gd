extends Node2D
## Rock Kombat: escenario de recital dibujado proceduralmente.
## Presentación independiente del combate: sin colisiones ni modificaciones de físicas.

const INK := Color("#090b16")
const NIGHT := Color("#14172a")
const PURPLE := Color("#302348")
const STAGE := Color("#292536")
const EDGE := Color("#ef4969")
const CYAN := Color("#54d6f3")
const GOLD := Color("#f9c967")

var beat: float = 0.0

func _process(delta: float) -> void:
	beat += delta
	queue_redraw()

func _draw() -> void:
	# Se extiende más allá de la cámara para que no queden bandas laterales.
	draw_rect(Rect2(-400, -160, 1200, 520), INK)
	draw_rect(Rect2(-400, 24, 1200, 152), NIGHT)
	draw_rect(Rect2(-400, 59, 1200, 101), PURPLE.darkened(0.60))
	# Truss de luces.
	draw_rect(Rect2(-400, 52, 1200, 6), Color("#3d4056"))
	for x in range(-380, 780, 28):
		draw_line(Vector2(x, 53), Vector2(x + 22, 58), Color("#74718d"), 1.0)
	# Pantalla trasera / corazón del escenario.
	draw_rect(Rect2(96, 67, 192, 82), Color("#0b0d20"))
	draw_rect(Rect2(99, 70, 186, 76), Color("#261a37"))
	draw_rect(Rect2(101, 72, 182, 72), Color("#190e2c"))
	# Ondas musicales abstractas detrás de los luchadores.
	for i in 19:
		var x := 111.0 + float(i) * 9.0
		var amp := 11.0 + absf(sin(float(i) * 0.93 + beat * 2.1)) * 24.0
		draw_rect(Rect2(x, 109.0 - amp * 0.5, 4, amp), CYAN.darkened(0.45 + float(i % 3) * 0.10))
	draw_line(Vector2(106, 109), Vector2(279, 109), EDGE.darkened(0.2), 1.0)
	# Reflectores con conos translúcidos, más intensos cerca del escenario.
	var swing := sin(beat * 0.65) * 18.0
	_spot(Vector2(45, 58), Vector2(126 + swing, 178), CYAN)
	_spot(Vector2(339, 58), Vector2(258 - swing, 178), EDGE)
	_spot(Vector2(192, 57), Vector2(192 + swing * 0.5, 175), GOLD)
	for x in [45, 192, 339]:
		draw_circle(Vector2(x, 57), 6.0, Color("#141522"))
		draw_rect(Rect2(x - 5, 54, 10, 5), Color("#6d6e87"))
		draw_circle(Vector2(x, 59), 2.5, GOLD)
	# Torres de parlantes en los laterales.
	_speaker(16)
	_speaker(349)
	# Siluetas de público y manos levantadas, detrás del ring.
	for i in 36:
		var x := -12.0 + float(i) * 12.0
		var y := 164.0 + float(i % 4) * 2.0
		draw_circle(Vector2(x, y), 6.0, Color("#0c0d19"))
		draw_line(Vector2(x, y + 4), Vector2(x + float(i % 3 - 1) * 3, 182), Color("#0c0d19"), 5.0)
		if i % 7 == 0:
			draw_line(Vector2(x + 2, y + 3), Vector2(x + 5, y - 13), Color("#0c0d19"), 2.0)
	# Piso de escenario (los pies de los luchadores quedan en y=180).
	draw_rect(Rect2(-400, 180, 1200, 160), STAGE)
	draw_rect(Rect2(-400, 179, 1200, 2), EDGE)
	for j in 5:
		var yy := 185.0 + float(j * j) * 1.6
		draw_line(Vector2(-400, yy), Vector2(800, yy), Color("#44364d"), 1.0)
	for i in range(-9, 17):
		var px := 192.0 + float(i) * 36
		draw_line(Vector2(192, 180), Vector2(px, 280), Color("#403747"), 1.0)
	# Luces de borde sin impedir la lectura de los sprites.
	draw_rect(Rect2(-400, 193, 1200, 2), Color("#393145"))

func _spot(start: Vector2, target: Vector2, tint: Color) -> void:
	var faded := Color(tint.r, tint.g, tint.b, 0.10)
	draw_colored_polygon(PackedVector2Array([
		start + Vector2(-3, 0), start + Vector2(3, 0),
		target + Vector2(34, 0), target + Vector2(-34, 0)
	]), faded)

func _speaker(x: float) -> void:
	draw_rect(Rect2(x, 113, 20, 55), Color("#070814"))
	draw_rect(Rect2(x + 2, 115, 16, 51), Color("#232237"))
	for y in [128.0, 151.0]:
		draw_circle(Vector2(x + 10, y), 7.0, Color("#090b18"))
		draw_circle(Vector2(x + 10, y), 4.0, Color("#3e4058"))
