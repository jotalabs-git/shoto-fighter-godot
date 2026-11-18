# Personajes 3D en Rock Kombat

## Dirección de arte

Figuras de plastilina con estética de stop motion. La silueta,
el peinado y la indumentaria identifican al músico desde la cámara
lateral. Caras, cejas y manos admiten una exageración mayor que el
resto del cuerpo. Las mejillas se esculpen con planos suaves y las
asimetrías y pliegues del rostro dan expresión incluso en reposo.
La piel y el pelo tienen acabado mate y los detalles de ropa siguen
la superficie de la prenda. Bruce es la primera aplicación de esta
dirección. La lectura de las poses se comprueba a escala de combate.

## Presentación en Godot

El Guitarrista y el Frontman se instancian desde GLB en la pelea. Un
`SubViewport` transparente contiene a ambos, una cámara ortográfica y
luces compartidas. La pasada se compone sobre el escenario y debajo de
los efectos de combate y el HUD. Godot sigue calculando impactos,
bloqueos, inputs, distancias y posiciones en 2D.

## Uso

```bash
godot --path .
godot --path . -- --sprites
godot --path . res://tools/blender/model_preview.tscn
```

La segunda ejecución usa el catálogo PNG. Si falta un GLB, su catálogo
o un clip requerido, la pelea vuelve a sprites para ambos luchadores.
También se puede elegir el modo en `GameConfig.fighter_presentation`
o en la propiedad `presentation_mode` de la escena de combate.
El visor independiente carga los dos modelos. Las flechas cambian de
clip y P alterna la referencia PNG.

## Exportación reproducible

```bash
tools/blender/run.sh export-glb guitarist
tools/blender/run.sh export-glb frontman
godot --headless --path . --editor --import --quit
bash scripts/check-linux.sh
```

El exportador abre las fuentes existentes y desactiva en memoria
las influencias IK de edición. Conserva las acciones útiles, construye
las poses complementarias en memoria y hornea los clips a 60 Hz. El
horneado aplana la jerarquía exportada de huesos para respetar las
escalas independientes del rig de Blender. El micrófono, el cable y
la guitarra conservan su anclaje y evitan la deformación acumulada en
la primera exportación. La salida incluye GLB y un catálogo JSON con
tiempos por pose, desplazamiento de los ciclos y marcas de ataque.
Los `.blend` conservan el mismo SHA-256 que al iniciar. Dos exportaciones
desde las mismas fuentes produjeron GLB y JSON idénticos byte por byte.
La exportación y los PNG anteriores se conservan como ruta separada.

## Espacio, cámara y acción

- Conversión de 34 unidades lógicas por metro. X coincide con el
  desplazamiento 2D, Y mide altura sobre el piso y Z define profundidad.
  Los dos modelos miran a +X en origen. Godot rota el nodo según
  el oponente y aplica una vista de tres cuartos leve. La orientación
  de los PNG se usa únicamente en su ruta de dibujo.
- La cámara 3D replica centro y zoom de la cámara de combate.
  Durante el agarre, el encuadre 3D comparte los límites de 1,38× y
  centro vertical de 119 unidades con la cámara del escenario. El
  encuadre regular se recupera después. Los ciclos de marcha y
  carrera avanzan según la distancia recorrida en 2D.
- El reloj del atacante selecciona la pose de sujeción de la víctima.
  Durante la llave, el centro de ambos puños define el punto de
  contacto con el torso rival. Solo se desplaza el nodo dibujado:
  la raíz 2D y sus cajas conservan la posición de combate.
  El daño y el sonido de liberación se emiten una vez en tick 12.
  Una interrupción previa cancela el agarre sin aplicar ese daño.
- El agarre usa LP + LK (U + J para P1, coma + N para P2) a corta
  distancia. Se acepta el segundo botón durante el arranque del primer
  golpe ligero, hasta 4 ticks según el golpe. Sirven ambos órdenes.
- La víctima toca el suelo en el tick 20 del lanzamiento y las
  extremidades se acomodan durante los ticks siguientes. El atacante
  recupera el control al contacto. El sonido de suelo se dispara al
  llegar a la pose de contacto. La caída
  de barrido tiene su propio clip. En los últimos 12 ticks de
  recuperación normal se ejecuta `getup`, sin ampliar la ventana
  normal de 40 ticks en suelo. En KO se completa la caída visual
  aunque el round congele el combate, y el personaje queda tendido.
  Blender mide la distancia del torso al punto más bajo del modelo
  en `down_hold` y valida que no exceda 0,075 m.
- El renderer se mantiene en GL Compatibility. glTF conserva color,
  metal y rugosidad. El acabado procedural de Blender se aproxima
  con un relieve compartido en GPU. En llvmpipe y softpipe el
  SubViewport limita su ancho a 960 y omite ese relieve y MSAA.
  Las capturas gráficas de este informe se hicieron con llvmpipe.
- Los puñetazos 3D encadenan guardia, carga, extensión y regreso.
  El hombro acompaña el giro del torso, el codo mantiene una flexión
  en la extensión y la muñeca sigue el arco del antebrazo. El Frontman
  golpea con la mano libre y conserva el micrófono en la otra. En
  marcha, carrera y patadas los brazos acompañan el equilibrio.
  `arm_motion.py` hornea longitudes fijas de brazo y antebrazo.
  Blender exporta los clips desde el segundo cero y Godot los importa
  a 60 Hz para alinear la extensión con el tick de impacto.

## Clips en cada GLB

| Categoría | Clips |
| --- | --- |
| Reposo y marcha | `idle`, `walk_fwd`, `walk_back`, `run`, `run_back` |
| Agacharse | `crouch_enter`, `crouch`, `crouch_exit` |
| Salto | `jump_start`, `jump`, `fall_air`, `land` |
| Normales de pie | `stand_lp`, `stand_mp`, `stand_hp`, `stand_lk`, `stand_mk`, `stand_hk` |
| Normales agachados | `crouch_lp`, `crouch_mp`, `crouch_hp`, `crouch_lk`, `crouch_mk`, `crouch_hk` |
| Normales aéreos | `jump_lp`, `jump_mp`, `jump_hp`, `jump_lk`, `jump_mk`, `jump_hk` |
| Guardia y bloqueo | `guard`, `guard_crouch`, `block_high`, `block_low` |
| Reacciones y especiales | `hurt`, `hurt_low`, `palm`, `upper`, `knee` |
| Llave | `throw`, `grabbed_hold`, `thrown_air` |
| Caída y recuperación | `knockdown`, `knockdown_low`, `down_hold`, `getup`, `ko_fall` |

## Pruebas y capturas

La prueba automatizada `test_combat_3d.gd` valida los 47 clips de
cada import, sus tracks, la orientación al cruzarse, cuatro
combinaciones de agarre junto a las paredes, sincronización en ticks
12 y 20, un único daño, limpieza del anclaje, barrido, contacto,
levantamiento, KO, throw tech e intento fallido. También instancia el
fallback explícito y un combate con un modelo inexistente.

```bash
xvfb-run -a godot --path . --audio-driver Dummy --resolution 960x540 \
  --fixed-fps 60 --script res://tools/blender/verify_match.gd -- \
  reports/character-art/3d/ajuste/capturas --throws --ko
xvfb-run -a godot --path . --audio-driver Dummy --resolution 960x540 \
  --fixed-fps 60 --script res://tools/blender/verify_match.gd -- \
  reports/character-art/3d/brazos/final --arms --ko --throws
xvfb-run -a godot --path . --audio-driver Dummy --resolution 1280x720 \
  --fixed-fps 60 --script res://tools/blender/verify_match.gd -- \
  reports/character-art/3d/final-sprites --sprites
godot --headless --path . --fixed-fps 60 \
  --script res://tools/blender/verify_match.gd -- \
  reports/character-art/3d/final-cpu --cpu --round
```

Los registros de importación, exportación y las capturas están en
`reports/character-art/3d/`. El verificador de capturas silencia
su instancia de audio. La suite normal también comprueba el banco
de sonidos, el HUD, el combate, las rondas y los inputs.

La exportación con Blender 5.0.1 y la importación con Godot 4.7.2
completaron el catálogo de 47 clips por personaje. Después del ajuste
de KO y del agarre, la suite Linux ejecutó 125 pruebas en 34 suites,
con cero errores y cero fallos. En OpenGL Compatibility, la escena
real reconoció los agarres iniciados con U y después J, y con N y
después coma, con 2 ticks entre los eventos físicos. También se
capturó el KO de ambos luchadores. Los registros se encuentran en
`reports/character-art/3d/ajuste/`. Las poses exportadas dejaron 0,022 m
entre el torso y el suelo para el Guitarrista y 0,052 m para el Frontman.
En la verificación de la migración, la pelea con sprites funcionó y la
ronda contra la CPU terminó con victoria de P1, con 520 de vida y P2
en cero.

Con la nueva animación de brazos, la suite ejecutó 126 pruebas sin
fallos. La prueba de articulaciones midió ambos segmentos de los
brazos en las marchas y puñetazos importados. La verificación gráfica
registró el golpe fuerte y la vuelta a guardia de ambos personajes,
los dos agarres y ambos KO. El video a 60 fps está en
`reports/character-art/3d/brazos/brazos.mp4`.

`agarres.png` recorre sujeción, vuelo, caída y levantamiento. La fila
superior corresponde al Guitarrista como atacante y la inferior al
Frontman. `comparacion.png` muestra 3D a la izquierda y PNG a la derecha
en reposo. En la captura 3D se distinguen los bordes de la silueta y
las piezas del vestuario. El PNG conserva las sombras y la textura que
hornea Blender, mientras que el volumen del GLB se ilumina en Godot.

## Archivos principales

| Área | Archivos |
| --- | --- |
| Exportación y visor | `tools/blender/run.sh`, `export_glb.py`, `poses_3d.py`, `arm_motion.py`, `model_preview.gd`, `model_preview.tscn` |
| Modelos y catálogos | `assets/models/guitarist.glb`, `guitarist.json`, `frontman.glb`, `frontman.json` y sus ajustes de importación |
| Presentación | `match/presentation/combat_3d.gd`, `fighter_3d_view.gd`, `match/match_manager.gd`, `globals/game_config.gd` |
| Estados del luchador | `fighter/fighter.gd`, `fighter/fighter.tscn`, `fighter/states/throw.gd`, `knockdown.gd`, `getup.gd` |
| Verificación | `tools/blender/verify_match.gd`, `test/integration/test_combat_3d.gd`, `test_throw_cinematic.gd`, `test_match_audio_and_facing.gd` |
