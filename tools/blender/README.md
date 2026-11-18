# Personajes de Rock Kombat en Blender

Blender **5.0** con Cycles en CPU, Bash y Python 3 del sistema. El
exportador y el validador usan la biblioteca estándar. Godot 4.4+ se usa
para importar y verificar en juego. En Linux sin escritorio, Xvfb permite
guardar capturas con el renderer real.

Ejecutá desde la raíz del repositorio. El lanzador busca `blender` en el
`PATH` y acepta `BLENDER=/ruta/al/binario` y `BLENDER_THREADS=4`.
Pasa los argumentos de cada script después del separador `--`.

## Generación y exportación

```bash
tools/blender/run.sh generate guitarist
tools/blender/run.sh render guitarist --actions idle walk_fwd stand_lp hurt
python3 tools/blender/validate_character.py guitarist

tools/blender/run.sh generate guitarist --full
tools/blender/run.sh render guitarist
python3 tools/blender/validate_character.py guitarist --complete

tools/blender/run.sh generate frontman --full
tools/blender/run.sh render frontman
python3 tools/blender/validate_character.py frontman --complete
```

`generate` reconstruye el archivo editable en `sources/<id>.blend`.
Guardá una copia con otro nombre antes de regenerar un archivo con
ediciones manuales. `generate --full` incluye el catálogo completo y
`generate` prepara las cuatro acciones iniciales. La malla en piezas de
plastilina, la armadura, los materiales, las luces y la cámara están en
el .blend. El editor de acciones de Blender permite seleccionar y editar
cada acción del `Rig`. `poses.py` define el storyboard, los joints y los
ticks por pose. `character_spec.json` define las paletas y la calibración.

`render` abre el .blend existente. Renderiza una pose al comienzo de cada
intervalo declarado, descarta metadatos variables de fecha y ruta,
valida la exportación propuesta en un directorio
temporal y solo entonces publica los PNG numerados y `manifest.json`.
`--actions` sirve para reemplazar acciones individuales manteniendo las
demás. Usá una ejecución a la vez por carpeta de salida. Cuando cambia
el .blend, reexportá las acciones editadas. Cuando cambia el modelo,
la cámara o las luces, reexportá todo. Si coinciden la fuente, la
versión de Blender y el manifiesto, se reutilizan los PNG validados.
`--force` vuelve a renderizar los seleccionados. Usá
`--output reports/character-art/prueba` para revisar fuera del juego y
`--diagnostics reports/character-art/rechazado` para guardar los
fotogramas de una exportación rechazada.

La cámara ortográfica exporta RGBA8 de **176 × 148**, con apoyo en
**[79, 136]** y frente hacia la derecha. El margen adicional en X
deja espacio para los derribos y las patadas extendidas. El eje se
valida proyectando el origen fijo. Cada intervalo del manifiesto está
en ticks de 60 Hz. Los ataques indican los índices de inicio del impacto
y de la recuperación para ajustar la pose visual al estado del combate.
Los efectos, hitboxes y tiempos lógicos pertenecen al motor de combate.

## Revisión

```bash
python3 tools/blender/contact_sheet.py assets/characters/guitarist \
  reports/character-art/guitarist.png idle:0 walk_fwd:2 stand_lp:1 hurt:0
python3 tools/blender/contact_sheet.py assets/characters/frontman \
  reports/character-art/frontman.png
bash scripts/check-linux.sh
xvfb-run -a godot --path . --audio-driver Dummy --resolution 768x432 \
  --fixed-fps 60 --script res://tools/blender/verify_match.gd -- \
  reports/character-art/dos-jugadores
xvfb-run -a godot --path . --audio-driver Dummy --resolution 768x432 \
  --fixed-fps 60 --script res://tools/blender/verify_match.gd -- \
  reports/character-art/cpu --cpu
godot --headless --path . --fixed-fps 60 \
  --script res://tools/blender/verify_match.gd -- reports/character-art/cpu --cpu --round
godot --headless --path . --fixed-fps 60 \
  --script res://tools/blender/verify_match.gd -- reports/character-art/dos-jugadores --match
```

Sin argumentos de pose, el mosaico muestra el fotograma central de
cada acción. Acompaña al PNG un JSON con índice y ubicación. La línea
horizontal marca el piso. La opción `--slice` del smoke test se usa cuando
el Guitarrista tiene cuatro acciones y el Frontman sigue con KFM.
La comprobación gráfica usa inputs programados y desactiva el audio de
su instancia. `--round` verifica el fin de una ronda contra CPU y
`--match` completa dos rondas en el modo local.

Si Godot muestra KFM después del render, corré primero
`godot --headless --path . --editor --import --quit` y verificá el set
con el validador y los tests. Los `.blend` viven en una carpeta con
`.gdignore` para que Godot cargue solo los sprites del juego. Si preparás
un preset de exportación de Godot, incluí los `manifest.json` dentro del
filtro de archivos sin recursos y las texturas cargadas por ruta.
