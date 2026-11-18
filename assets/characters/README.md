# Personajes originales de Rock Kombat

Cada personaje tiene su carpeta, por ejemplo `guitarist/` o `frontman/`.
El cargador busca `manifest.json` en la carpeta registrada en
`core/character_registry.gd`. **Si no hay manifest o falta algún PNG,
usa el sprite KFM temporalmente**; no se altera el combate.

El formato del manifiesto es compatible con
`assets/kfm/manifest.json`:

```json
{
  "canvas": [137, 148],
  "axis": [55, 139],
  "anims": {
    "idle": {"frames": 2, "durs": [8, 8], "loop": true},
    "stand_lp": {"frames": 3, "durs": [3, 4, 5], "loop": false}
  }
}
```

Para este ejemplo, incorporar:
`guitarist/idle/000.png`, `guitarist/idle/001.png`,
`guitarist/stand_lp/000.png`, `001.png`, `002.png`.
Los PNG deben ser RGBA con fondo transparente y resolución consistente.
`axis` es la coordenada del apoyo de pies respecto del lienzo.
Las duraciones son ticks a 60 FPS.

Para la versión definitiva conviene exportar todos los nombres
de animación presentes en el manifiesto de KFM. La ausencia de una
animación concreta se muestra en idle sin modificar el tiempo lógico
del golpe.

IDs reservados: `guitarist` y `frontman`. De momento mantienen
estadísticas y ataques de prueba: todavía no incluyen arte original.
Para hacerlos aparecer en un combate, cambiar los `character_id`
de Player1/Player2 en `match/match.tscn`; el HUD obtiene los nombres
del registro.

## Flujo Blender → Godot

1. Modelar y animar con pies fijos en el punto de referencia.
2. Renderizar cámara ortográfica, iluminación y transparencia consistentes.
3. Exportar secuencia PNG por animación, empezando por `000.png`.
4. Generar el manifiesto con cantidad de frames y duraciones.
5. Comprobar que cada animación se reproduce y que las cajas de colisión
   (F1) continúan alineadas con el cuerpo.

El arte original debe conservar su propia licencia. Los recursos KFM
existentes siguen sujetos a sus condiciones no comerciales.
