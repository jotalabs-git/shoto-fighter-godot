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

El campo opcional `pixels_per_unit` indica cuántos píxeles del PNG
corresponden a cada unidad del lienzo. Con `3`, un `canvas` de
`[176, 148]` requiere PNG de 528 × 444. `canvas` y `axis` siguen en
unidades lógicas. Sin el campo, Godot interpreta el set como 1×.

Para la versión definitiva conviene exportar todos los nombres
de animación presentes en el manifiesto de KFM. La ausencia de una
animación concreta se muestra en idle sin modificar el tiempo lógico
del golpe.

`guitarist` y `frontman` incluyen sus propios sprites y son los luchadores
de la escena de combate. Conservan los perfiles de Kaze y Homura,
respectivamente. El HUD obtiene sus nombres del registro.

Las acciones de ataque pueden declarar `phases: [impacto, recuperación]`
con los índices de inicio de esos tramos, empezando desde cero. Godot
ajusta la pose al tick del ataque actual, incluidos alias y hitstop.

## Flujo Blender → Godot

1. Modelar y animar con pies fijos en el punto de referencia.
2. Renderizar cámara ortográfica, iluminación y transparencia consistentes.
3. Exportar secuencia PNG por animación, empezando por `000.png`.
4. Generar el manifiesto con cantidad de frames y duraciones.
5. Comprobar que cada animación se reproduce y que las cajas de colisión
   (F1) continúan alineadas con el cuerpo.

Las fuentes editables están en [tools/blender/sources](../../tools/blender/sources).
Los [comandos de generación](../../tools/blender/README.md) y
el [informe de G0–G5](../../docs/personajes-blender-qa.md) describen el flujo verificado.
Los recursos KFM existentes siguen sujetos a sus condiciones no comerciales.
