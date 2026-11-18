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
  faltantes de KFM. Conservó los 19 PNG de G2.
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
