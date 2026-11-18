# Rock Kombat · Producción y QA de personajes

Los comandos se ejecutaron en Linux desde la raíz del repositorio. Las
capturas y los logs locales se guardan en `reports/character-art/`.
Los comandos de reproducción están en [tools/blender/README.md](../tools/blender/README.md).

## G0 · Auditoría

- `main` avanzó 13 commits hasta `f42e188`, donde estaba la guía. Se
  reaplicaron las ediciones locales de `project.godot` conservando el
  nombre Rock Kombat. El UID local de ConcertStage quedó en el árbol.
- `blender --version` dio 5.0.1. El Python integrado y el del sistema son
  3.14.4. `godot --version` dio 4.7.2.stable.official. Hay 411 GiB libres
  según `df -h .`. El render CPU y Xvfb están disponibles.
- Se leyeron el README de personajes, los cargadores, el registro, los
  perfiles, las escenas de luchador y combate, el manifiesto KFM y la
  prueba de fallback. KFM lista 26 acciones. `Fighter` consume 24, con
  alias para golpes aéreos y agachados. `getup` y `hurt_low` quedan
  disponibles en el catálogo de exportación.
- `bash scripts/check-linux.sh` aprobó la importación y los 101 tests
  de partida. Evidencia en `g0-godot.log`. Esta etapa no genera poses.

## G1 · Primer modelo

- Se implementaron la generación con `bpy`, el rig editable de 15 huesos,
  la escultura por piezas, cámara fija, luces, exportador, validador y
  mosaico. Fuente en `tools/blender/sources/guitarist.blend`.
- `tools/blender/run.sh generate guitarist` guardó la fuente. El primer
  intento falló porque la escena vacía no tenía `World`. El generador
  ahora crea el mundo del estudio antes de configurar Cycles.
- `tools/blender/run.sh render guitarist --output reports/character-art/g1
  --actions idle stand_lp` verificó 8 PNG en 1,3 s. El mosaico
  `g1-lookdev.png` muestra el perfil en guardia y el jab activo, a escala
  nativa. Se revisaron perfil hacia la derecha, guitarra, transparencia
  y piso de referencia. Altura de la figura en guardia ≈114 px de
  textura, ≈97 unidades del juego con el factor 0,85.

## G2 · Primer personaje en Godot

- `tools/blender/run.sh render guitarist --actions idle walk_fwd stand_lp hurt`
  exportó 19 PNG en 2,9 s. `python3 tools/blender/validate_character.py guitarist`
  aprobó las cuatro acciones. `g2-poses.png` muestra guardia, caminata,
  impacto y reacción. El eje proyectado se verificó en [79, 136].
- La primera importación detectó el .blend como escena 3D y abortó
  antes de importar los PNG. `.gdignore` separó las fuentes y los
  reportes de los recursos del juego. La reimportación procesó los 19
  PNG. Se ajustó el tinte solo cuando se cargan sprites propios.
- El smoke gráfico con `--slice` cargó el Guitarrista y KFM para P2.
  Verificó caminata, reflejo, pose activa del jab, 30 puntos de daño
  en ambos sentidos y reacción. Se inspeccionaron las capturas de
  `g2-match/`, incluido el overlay de cajas y el apoyo sobre el
  piso del recital. Xvfb con llvmpipe avisó que no admite cambiar V-Sync.
- La segunda ejecución de `bash scripts/check-linux.sh` aprobó los 102
  tests, incluida la carga del PNG propio y el fallback de Kaze.

## G3 · Catálogo del Guitarrista

- `tools/blender/run.sh generate guitarist --full` reconstruyó la fuente.
  `tools/blender/run.sh render guitarist --actions` recibió los 22 nombres
  faltantes de KFM. Añadió 94 PNG en 16,4 s y conservó los 19 PNG de G2.
- El validador bloqueó la primera exportación porque `knockdown/003.png`
  y `getup/000.png` tocaban el borde inferior. Se elevó la pose caída con
  apoyo de la bota y se repitió la exportación. `g3-render-rejected.log`
  conserva el diagnóstico. `g3-render.log` registra la corrida válida.
- Se verificó el catálogo completo con `validate_character.py guitarist --complete`
  y se revisó `g3-catalogo.png`, incluidas poses agachadas, contacto y
  derribo. La importación headless aprobó.
- Se completó una ronda contra CPU en el smoke headless con `--cpu --slice
  --round`. P1 ganó con 400 de vida, P2 terminó en 0. La corrida gráfica
  produjo una captura del primer intercambio en `g3-cpu/cpu-contacto.png`.

## G4 · Frontman

- `tools/blender/run.sh generate frontman` y `render frontman --actions
  idle stand_lp hurt` produjeron 11 PNG en 1,7 s. Se revisó el mosaico
  `g4-preview.png` y se comprobó la carga de ambos sets independientes
  en la escena real con `verify_match.gd`.
- La primera exportación completa rechazó un cuadro del puñetazo medio
  y cuatro cuadros de caída o recuperación. Se desactivó la herencia de
  escala entre huesos y se compensó el volumen del peinado en la caída.
  El render completo siguiente exportó las 26 acciones en 16,1 s.
- El validador aprobó **113 PNG por luchador**. El mosaico
  `g4-catalogo.png` muestra el set del Frontman con cresta, chaqueta coral
  y micrófono. Se inspeccionaron escala, reflejo, guardia y golpes en
  `g4-match/`.
- El smoke de dos jugadores verificó movimiento, pose activa y daño en
  ambas direcciones. La ronda headless vs CPU terminó en KO con
  P1 en 400 de vida y P2 en 0. Los avisos del smoke incluían V-Sync
  bajo Xvfb y objetos WAV al cerrar la corrida acelerada.

## G5 · Integración final

- Se pulieron los especiales, el pulso del Frontman en guardia y el
  material de ambos con 24 muestras de Cycles. Las acciones de ataque
  llevan marcadores de impacto y recuperación. La presentación usa el
  tick real del ataque y mantiene la pose en hitstop. Los alias de
  golpes aéreos, agachados y especiales conservan sus tiempos lógicos.
- `tools/blender/run.sh generate <id> --full` y `render <id>` se
  ejecutaron para ambos luchadores. Las exportaciones completas
  tardaron 30,4 s y 29,6 s respectivamente, incluida validación.
  Cada fuente ocupa unos 463 KiB. Los PNG de ambos suman unos 4,6 MiB.
- `python3 tools/blender/validate_character.py <id> --complete` aprobó
  113 PNG por luchador. Una copia con un hueco de numeración se rechazó
  e identificó tanto `idle/001.png` faltante como `idle/004.png` extra.
- La regeneración de guardia, jab y caída del Guitarrista produjo
  los mismos píxeles en 12 fotogramas. La primera comparación binaria
  detectó marcas de tiempo y rutas de Blender en los PNG. El exportador
  ahora las retira. Los 12 PNG coinciden byte por byte al repetir la prueba.
- Blender abrió ambas fuentes y confirmó la misma jerarquía de 15
  huesos, 26 acciones editables por fuente, cámara ortográfica y cierre
  de los siete bucles declarados. Evidencia en `g5-sources.log`.
- La importación headless y la suite `bash scripts/check-linux.sh`
  aprobaron **103 pruebas en 29 suites**, incluidas carga propia,
  fallback a KFM, HUD, bloqueos, proyectiles, golpes, IA y rondas.
  Una copia limpia del índice de Git aprobó los mismos 103 tests.
  Evidencia en `g5-godot.log` y `g5-clean-tree.log`.
- Los smokes con Xvfb revisaron ambos sets reflejados, impactos,
  hitstop y reacción. La prueba local headless con `--match` terminó
  **2–0**. Contra CPU, la ronda headless terminó por KO con **400–0**
  de vida y las capturas de Xvfb registraron un intercambio. Las
  corridas gráficas usan entradas programadas, audio desactivado
  en el verificador y llvmpipe, que avisó sobre V-Sync.
- Capturas finales en `g5-match/` y `g5-cpu/`. Los mosaicos
  `g5-guitarist-acciones.png` y `g5-frontman-acciones.png`
  muestran guardia, jab, reacción, agachado, patada, especiales y caída.
  El perfil inicial de 128 px está en `g1-perfil-128.png`.

### Inventario final

`getup` y `hurt_low` están disponibles para reutilizar en Blender
y en el manifiesto. El selector actual de estados usa `knockdown`
y `hurt`.

| Acción | PNG por luchador | Ticks Guitarrista | Ticks Frontman |
| --- | ---: | ---: | ---: |
| `idle` | 4 | 26 | 18 |
| `walk_fwd` | 8 | 24 | 24 |
| `walk_back` | 8 | 24 | 24 |
| `crouch` | 1 | 1 | 1 |
| `jump` | 5 | 37 | 37 |
| `run` | 6 | 18 | 18 |
| `stand_lp` | 4 | 14 | 14 |
| `stand_mp` | 4 | 21 | 21 |
| `stand_hp` | 4 | 31 | 31 |
| `stand_lk` | 5 | 16 | 16 |
| `stand_mk` | 5 | 25 | 25 |
| `stand_hk` | 5 | 35 | 35 |
| `crouch_lp` | 4 | 13 | 13 |
| `crouch_mp` | 4 | 20 | 20 |
| `crouch_lk` | 5 | 14 | 14 |
| `crouch_hk` | 5 | 34 | 34 |
| `guard` | 1 | 1 | 1 |
| `guard_crouch` | 1 | 1 | 1 |
| `hurt` | 3 | 12 | 12 |
| `hurt_low` | 2 | 10 | 10 |
| `knockdown` | 4 | 40 | 40 |
| `getup` | 4 | 32 | 32 |
| `throw` | 5 | 29 | 29 |
| `palm` | 5 | 43 | 43 |
| `upper` | 5 | 35 | 35 |
| `knee` | 6 | 31 | 31 |
| **Total** | **113** | | |

### Commits

- G0–G2 · `078c7f0` · Pipeline y primer personaje en Godot.
- G3 · `e8d85ed` · Catálogo completo del Guitarrista.
- G4 · `d2368c7` · Frontman sobre el rig compartido.
- G5 · `feat(art): polish and verify both Blender fighters`.

## Rediseño del Guitarrista · Muñeco articulado

- La fuente `tools/blender/sources/guitarist.blend` incluye un rostro
  modelado de ambos lados, cabello con volumen frontal y posterior,
  y una figura completa con materiales mate. La chaqueta y el pantalón
  se deforman por pesos de armadura.
- La fuente abre en Pose Mode. El esqueleto conserva 15 huesos de la
  animación original y suma ocho controles manuales (cuatro objetivos
  y cuatro polos). La prueba de Blender movió las cuatro cadenas IK
  y comprobó el seguimiento de manos y pies.
- `tools/blender/run.sh generate guitarist --full` y `render guitarist`
  reexportaron 113 PNG en 26 acciones. El validador comprobó transparencia,
  encuadre y catálogo completo. Tras ajustar la vista inicial de Blender,
  se reprodujeron 12 PNG de guardia, golpe y caída byte por byte.
- `bash scripts/check-linux.sh` aprobó 103 tests. El smoke gráfico en
  Godot comprobó la caminata, el golpe y la reacción de ambos personajes.
  Las vistas de frente, tres cuartos y espalda, el esqueleto y la
  captura de combate están en `reports/character-art/guitarist-sculpt/`.

### Guantes y arnés de guitarra

El Guitarrista lleva guantes de boxeo de cuero color ciruela, con pulgar
y puño acolchado. La guitarra va en la espalda en un arnés de dos tiras.
El especial `palm` ahora se lee como un empuje de ambos puños.
Se conservaron los tiempos y el encuadre del juego.

Se regeneró el .blend y el validador aprobó los **113 PNG de 26 acciones**.
La prueba de Blender confirmó las cuatro cadenas IK. Se revisaron
guardia, jab, especial y caída, y las vistas de estudio en
`reports/character-art/guitarist-gloves/`.
La última corrida de `bash scripts/check-linux.sh` aprobó **103 pruebas**.
El smoke gráfico confirmó caminata, pose de impacto, hitstop y reacción
en la escena de dos jugadores.

### Dirección de arte · Rock callejero

Se esculpió un mechón grueso hacia adelante sobre un lateral rebajado,
con ceja alzada, párpados pesados, sonrisa torcida y barba corta.
La chaqueta es más corta, con cierre diagonal y una sola hombrera violeta.
La hombrera y los guantes tienen marcas suaves de huella en el material.
La guardia carga la pierna trasera y mantiene un guante alto.

Primero se renderizó solo `idle`. Se comprobó su lectura en una copia del
escenario a 384 × 216 y se comparó con la versión anterior. Con esa vista
revisada se exportó el catálogo completo. El encuadre, el eje y las
duraciones del manifiesto se conservaron. Las cuatro cadenas IK
se calibraron y probaron desde la nueva guardia.

Evidencias en `reports/character-art/guitarist-style/` con vistas
de estudio, comparación a resolución nativa y hoja de poses.

El validador aprobó 113 PNG en 26 acciones y `scripts/check-linux.sh`
aprobó las 103 pruebas. El smoke gráfico final a 384 × 216 verificó
caminata, jab, hitstop y reacción. La comparación final está en
`guitarist-style/comparativa-384.png` (antes a la izquierda).
