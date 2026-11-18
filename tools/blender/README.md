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

La cámara ortográfica exporta RGBA8 de **528 × 444**, con densidad
**3×** sobre el lienzo lógico de **176 × 148**. El eje lógico es
**[79, 136]** para el Guitarrista y **[97, 136]** para el Frontman.
La cámara exporta al Guitarrista hacia la derecha y al Frontman hacia
la izquierda. Godot orienta el dibujo según el rival. Se valida el eje
proyectando el origen fijo en píxeles de textura. Cada intervalo del manifiesto está
en ticks de 60 Hz. Los ataques indican los índices de inicio del impacto
y de la recuperación para ajustar la pose visual al estado del combate.
Los efectos, hitboxes y tiempos lógicos pertenecen al motor de combate.

## Revisión

### Posar los personajes en Blender

Las fuentes del Guitarrista y el Frontman se abren en Pose Mode. En **Object Properties →
Custom Properties** del objeto `Rig`, poné `IK_hands` o `IK_feet` en 1 para
posar brazos o piernas. En la vista 3D, mové los controles azules para
colocar manos y pies. Los verdes orientan codos y rodillas. La chaqueta y
el pantalón tienen pesos de deformación en hombros, codos, caderas y
rodillas. La guitarra tiene su propio hueso.

Volvé a 0 para editar o reproducir la acción original. El exportador
desactiva estos controles en memoria al renderizar las acciones del juego.

### Ver los sprites en juego

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


## Nitidez en Godot

El lienzo lógico conserva el tamaño de cada luchador. Godot compensa la
densidad al dibujar el sprite y al trasladar el ancla de pies a
coordenadas de textura. Los sets de alta densidad usan filtro lineal
propio para el zoom fraccionario de la cámara. Los sets de densidad 1
usan vecino más cercano.

Para revisar una exportación compará el PNG nativo y una captura de la
misma pose, resolución y distancia de cámara. Un cambio de densidad,
lienzo o eje requiere reexportar todas las acciones de ese personaje.

## Modelos 3D para Godot

```bash
tools/blender/run.sh export-glb guitarist
tools/blender/run.sh export-glb frontman
godot --path . res://tools/blender/model_preview.tscn
```

La exportación usa los .blend existentes en modo lectura y escribe
`assets/models/<id>.glb` y su catálogo JSON. Ver
[arquitectura, clips y verificación](../../docs/personajes-3d.md).

## Ozzy

El archivo editable está en `tools/blender/sources/ozzy.blend`.
Incluye el rig compartido, controles IK y poses de combate. La
exportación añade el catálogo completo de 47 clips a 60 Hz.

```bash
tools/blender/run.sh export-glb ozzy
godot --path . res://tools/blender/model_preview.tscn -- --ozzy
```

En el visor, las flechas cambian el clip y A/D giran el personaje.
Ozzy está disponible en el visor y se puede instanciar como luchador
de prueba con `character_id = "ozzy"`. La pelea predeterminada sigue
usando al Guitarrista y al Frontman. Para reconstruir la fuente desde
el código del escultor, usá `tools/blender/run.sh generate ozzy --full`.
Ese comando sobrescribe `ozzy.blend`.

La versión con la sonrisa ajustada se revisó de perfil y de tres
cuartos en Blender. En Godot, Ozzy cargó los 47 clips y conectó un
golpe fuerte en una pelea de prueba. Las 127 pruebas de Linux pasaron.

## Bruce Dickinson

El modelo editable está en `tools/blender/sources/bruce.blend`.
La Union Jack sigue la superficie de ambas mangas y usa sus mismos
pesos de deformación. Las solapas, el cierre, los broches y la hebilla
se ajustan a la geometría de la campera. El GLB usa el rig compartido
y el catálogo de 47 clips a 60 Hz.

```bash
tools/blender/run.sh export-glb bruce
godot --path . res://tools/blender/model_preview.tscn -- --bruce
```

En el visor, las flechas cambian de clip y A/D giran el personaje.
Para probarlo en combate se puede usar `character_id = "bruce"`.
Dos exportaciones produjeron el mismo GLB y catálogo JSON. En Godot
cargaron los 47 clips, Bruce conectó un golpe fuerte en una pelea de
prueba y la suite Linux pasó las 127 pruebas.

## Presentadora de rounds

La figura editable está en `tools/blender/sources/presenter.blend`.
Tiene tres acciones a 60 Hz: reposo, caminata y presentación. Entrando
a una partida desde la selección de personajes, usa el mismo escenario
3D del combate. Entra desde fuera del borde izquierdo, levanta un
cartel con el número de round y cruza el borde derecho antes de
habilitar los controles y el reloj. El recorrido se calcula con el
ancho de cámara al iniciar cada round. Las partidas con sprites usan
la introducción corta del HUD.

```bash
tools/blender/run.sh generate presenter
tools/blender/run.sh export-glb presenter
```
