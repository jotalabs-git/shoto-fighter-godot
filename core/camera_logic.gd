class_name CameraLogic
extends RefCounted

## Cálculo puro de la cámara: centro (punto medio de los 2 jugadores) y zoom según
## la distancia entre ellos, acotado entre min_zoom y max_zoom. Devuelve [center_x, zoom].
## En Godot, zoom > 1 acerca y zoom < 1 aleja.

static func compute(x1: float, x2: float, view_w: float, min_zoom: float, max_zoom: float, margin: float) -> Array:
	var center: float = (x1 + x2) / 2.0
	var dist: float = abs(x1 - x2)
	var needed: float = dist + margin * 2.0
	var zoom: float = view_w / maxf(needed, 1.0)
	zoom = clampf(zoom, min_zoom, max_zoom)
	return [center, zoom]

## Encuadre cinematografico temporario para agarrones confirmados.
## Sigue el punto medio, pero ignora el limite de zoom del combate
## normal; no altera la simulacion ni la posicion de los luchadores.
static func throw_closeup(x1: float, x2: float, zoom: float) -> Array:
	return [(x1 + x2) / 2.0, maxf(zoom, 1.0)]
