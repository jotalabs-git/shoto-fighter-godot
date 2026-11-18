# Rock Kombat — Guía ejecutable para Codex: personajes 3D en Blender → sprites 2D en Godot

**Estado:** especificación y prompts de implementación, **no** modelos ya creados.  
**Destino:** este repositorio, trabajando con Codex y Blender local en Kubuntu.  
**Prioridad:** una demo jugable con **un personaje realmente nuevo** antes de producir el segundo.  
**Alcance inicial:** personajes originales **El Guitarrista** (`guitarist`) y **El Frontman** (`frontman`). Mantener el combate actual, no crear un motor nuevo.

## 0. Instrucción central para el agente

> Trabajá sobre el repositorio existente, inspeccioná el código antes de generar arte y construí un pipeline **reproducible, incremental y determinista** para modelar, animar y renderizar personajes en Blender mediante Python (`bpy`). Primero producí una prueba de concepto con `idle`, `walk_fwd`, `stand_lp` y `hurt` de `guitarist`; verificá la carga en Godot. Solamente después completá su set de animaciones y pasá a `frontman`. La jugabilidad ya fue aprobada: no modificar inputs, hitboxes, frame data, IA, físicas ni el sistema de rondas salvo si una incompatibilidad real obliga a corregirla con tests.

**Definición de terminado:** Blender fuente editable + script generador + export PNG + manifiesto válido + importación en Godot + pruebas + capturas comparativas + combate jugable sin errores. No alcanza con crear un render vistoso.

---

## 1. Estado del proyecto que Codex debe corroborar al comenzar

Los siguientes archivos son la **fuente de verdad**. Releerlos al ejecutar: pueden haber cambiado desde la redacción de esta guía.

| Archivo | Responsabilidad |
|---|---|
| `core/character_registry.gd` | IDs, nombre visual, carpeta, tinte. IDs ya registrados: `guitarist`, `frontman`, `kaze`, `homura`. |
| `core/character_frames.gd` | Carga `assets/characters/<id>/manifest.json` y PNG numerados; cachea `SpriteFrames`. Si falta o falla el recurso, cae a KFM. |
| `core/kfm_frames.gd` y `assets/kfm/manifest.json` | Referencia real para nombres de animaciones, duraciones y eje de pies. |
| `fighter/fighter.gd` | Determina animación a partir del estado; asigna `sprite.offset = -CharacterFrames.get_axis(character_id)`; si falta una animación, usa `idle`. |
| `fighter/fighter.tscn` | Nodo `AnimatedSprite2D`, rig alternativo y colisiones. |
| `core/characters.gd` | Estadísticas, especiales y roles jugables. No alterar en esta etapa. |
| `match/match.tscn`, `match/match_manager.gd` | Escenario, escala, cámara, posiciones y rounds. |
| `test/unit/test_character_registry.gd` | Test actual de fallback: **debe actualizarse** cuando existan PNG propios; no dejar una prueba que exija que no hay arte. |
| `assets/characters/README.md` | Contrato actual de importación de sprites. |

**Datos técnicos verificados al redactar:**

- Viewport lógico: **384 × 216** (`project.godot`), ampliado visualmente en ventana.
- Combate a **60 ticks/segundo**.
- Suelo lógico en **y = 180**; altura de hurtbox normal **96 unidades** (`fighter/fighter.gd`). No hacer personajes visualmente gigantes con respecto al cuerpo que golpea.
- `fighter.gd` usa `SPRITE_SCALE = 0.85`, da vuelta el sprite con `sprite.scale.x = SPRITE_SCALE * facing()`, y reproduce un único set por `character_id`.
- Referencia actual KFM: lienzo **137 × 148 px**, `axis = [55,139]`; esto es **referencia**, no requisito de tamaño idéntico para personajes nuevos.
- Un manifiesto tiene `canvas`, `axis`, `anims`. Cada animación declara `frames`, `durs` y `loop`. Las duraciones están medidas en ticks a 60 FPS; cada PNG se llama `000.png`, `001.png`, etc.
- Para personajes propios se busca **`idle` obligatorio**; animaciones restantes pueden llegar por fases. El fallback actualmente es por **set completo** ante fallos de carga, o por **animación a idle** cuando falta un nombre; NO mezcla frames nuevos y KFM dentro de una misma animación.
- `frontman` reutiliza el perfil Homura (rápido/agresivo); `guitarist` reutiliza el perfil Kaze (control de distancia). No cambiarlo por motivo estético.

### Nombres de animaciones a respetar

Copiar del manifiesto real de KFM antes de exportar. El inventario existente incluye:

```text
idle, walk_fwd, walk_back, crouch, jump, run,
stand_lp, stand_mp, stand_hp, stand_lk, stand_mk, stand_hk,
crouch_lp, crouch_mp, crouch_lk, crouch_hk,
guard, guard_crouch, hurt, hurt_low,
knockdown, getup, throw, palm, upper, knee
```

**Atención:** el código de Fighter puede solicitar otras variaciones para golpes aéreos usando alias de animaciones de pie, y puede usar `idle` para movimientos no mapeados. No inventar nombres no consumidos por `fighter.gd`. Mantener la correspondencia entre nombres, arranque de golpe, extensión y recuperación; si un anim de 3D dura menos o más que la ventana de gameplay, muestrear poses para **acompañar** esa ventana, no cambiar los frames lógicos del ataque.

---

## 2. Dirección de arte y alcance

**Estilo:** juego 2D de lucha inspirado en el dinamismo de Street Fighter, con personajes **3D caricaturescos renderizados a sprites**, apariencia de plastilina / stop motion artesanal. Inspiración tonal en la caricatura grotesca de programas de combates de celebridades, **sin copiar modelos, personajes ni diseños protegidos de terceros**.

**Material:** plastilina mate con roughness alta, pequeñas imperfecciones de superficie y siluetas legibles. Nada de piel fotorrealista, pelo de hebras finas, accesorios ultradetallados ni texturas fotográficas. **Primero lectura de silueta en 96 px; después detalle.**

**Proporciones de partida** (ajustables según la captura de prueba): cabezas 25–32 % de la altura total, manos y pies ligeramente grandes, torso ancho/legible, extremidades expresivas. El personaje debe verse inequívocamente como músico desde lejos.

**Cámara:** una sola cámara **ortográfica fija**, vista de perfil con ligera lectura frontal (por ejemplo 10–15°), SIN perspectiva cambiante ni giros espontáneos. El personaje base mira a la **derecha**, como KFM. Godot lo refleja cuando mira a la izquierda; evitá texto, logos, grabados o instrumentos que se vuelvan incorrectos al espejarse.

**Iluminación:** key suave cálida + fill fría + rim sutil; fondo transparente con `film_transparent`; sombra de contacto opcional dentro de los sprites, sin pintar el fondo. Color management y configuración de render constantes. No alterar cámara, escala, exposición ni materiales entre animaciones.

**Rendimiento:** diseñar una escena liviana, materiales procedurales y pocos objetos. No utilizar simulaciones de telas, pelo, fluidos ni partículas complejas para la primera demo. Mantener los blends, geometría y animaciones editables.

### Personaje A: El Guitarrista (primero)

- **Rol:** técnico/zoner; postura calculadora, confianza serena, movimientos con timing definido.
- **Silueta:** melena larga volumétrica en mechones grandes, chaqueta oscura de escenario, pantalón entallado, botas grandes, gesto desafiante. Cabeza expresiva, nariz/cejas muy legibles.
- **Paleta:** carbón, violeta profundo, celeste eléctrico y un acento metalizado cálido; contraste claro respecto del escenario oscuro.
- **Instrumento:** guitarra eléctrica caricaturizada **propia** (cuerpo simple y distintivo, mango exagerado), atada con correa. En posición de combate no debe atravesar cara, piernas ni tapar el golpe.
- **Ataques:** jab con mano libre (`stand_lp`), golpes fuertes con movimiento amplio de brazo/hombro; `palm` se lee como riff/onda sonora; `upper` como levantada teatral del mango; `knee` como giro/rodillazo. **Efectos y proyectiles siguen siendo los existentes** en el MVP.
- **Lectura:** manos y instrumento deben distinguirse a la escala final sin ocupar toda la pantalla.

### Personaje B: El Frontman (después de validar A)

- **Rol:** rushdown; pose extrovertida, provocadora, aceleraciones fuertes.
- **Silueta:** pelo alto con mechones gruesos, mandíbula y cejas exageradas, chaqueta corta brillante y pantalón ajustado, botas robustas; contraste claro con A.
- **Paleta:** rojo coral, magenta, marfil sucio y negro.
- **Instrumento/objeto:** micrófono de mano **sin cable simulado** en el primer pase; pie de micro opcional como accesorio para remates posteriores, no en todos los ataques.
- **Ataques:** puñetazos que parecen gestos de show, patadas dinámicas, `palm` como grito sónico visual, `upper` como salto espectacular. No modificar daño ni proyectiles todavía.
- **Lectura:** que no parezca el mismo modelo recoloreado; diferenciar forma de cráneo, peinado, torso, postura y timing de idle.

### Consistencia entre ambos

Crear **un rig humanoide reutilizable** (mismos nombres de huesos / jerarquía), pero geometrías y expresiones distintas. Reusar acciones base donde sirva; personalizar idle, ataques especiales y reacción. No recrear desde cero todo el esqueleto para B.

---

## 3. Contrato de archivos y transformaciones (obligatorio)

**Guardar fuentes editables separadas del export de juego:**

```text
tools/blender/
  generate_character.py      # crea/actualiza .blend por personaje con bpy
  render_character.py        # export por acciones, manifiesto y validación
  character_spec.json        # parámetros declarativos, nombres de acciones, cámara
  README.md                  # dependencias, comandos y troubleshooting
assets/characters/
  guitarist/
    guitarist.blend           # fuente; alternativamente tools/blender/sources/
    manifest.json
    idle/000.png
    idle/001.png
    walk_fwd/000.png
    stand_lp/000.png
    ...
  frontman/
    frontman.blend
    manifest.json
    idle/000.png
    ...
reports/character-art/        # renders de contacto, logs, QA; evitar binarios pesados en git si son solo reportes
```

Se permite ubicar los `.blend` en `tools/blender/sources/` si se documenta la convención. Evitar generar duplicados o caches en `src` o carpetas de código. Asegurar `.gitignore` para renders temporales y backups `.blend1`, **sin ignorar** los sprites y manifests finales.

**Reglas del exportador:**

1. Blender es la fuente, nunca el sprite pintado a mano como único recurso.
2. Renderizar PNG **RGBA** con transparencia real y misma resolución/encuadre para **todos los frames y acciones de un personaje**.
3. Mantener mismo `axis` (pies) para todas las animaciones; el anchor queda fijo en el lienzo aunque salte, se agache o caiga. No recortar cada PNG automáticamente al bounding box.
4. Proyectar la posición del origen del personaje sobre la cámara y calcular `axis` de modo reproducible (o usar calibración declarada y validarla). El ancla no debe variar por pose. No recentrar la imagen por fotograma.
5. Como punto de partida, probar **137×148 px y [55,139]** o una resolución equivalente con anchor ajustado; comparar en captura con KFM y la hurtbox. Elegir resolución final por lectura y tamaño en pantalla, no por seguir ciegamente los números de KFM.
6. Una sola proyección para ambos luchadores y escala comparable; evitar que el instrumento altere el ancla o la distancia de pies.
7. `frames` debe ser igual al número real de PNG consecutivos; `len(durs) == frames`; cada `dur` debe ser positiva; `loop` booleano.
8. Para animaciones no loop, primer frame = anticipación, intermedios = impacto / pose clave, últimos = recuperación; para `idle` y caminar, bucle sin salto perceptible.
9. Sin imágenes/fotos/archivos descargados arbitrariamente, ni servicios de IA externos. Geometría/materiales originales en Blender.
10. Script Python idempotente: ejecutar dos veces con mismos inputs no multiplica objetos ni cambia el resultado. Limpiar/crear colecciones gestionadas por script y fijar semillas si hay ruido procedimental.

**Cuidado con pipeline de carga actual:** `CharacterFrames._build` retorna `null` si falta cualquier PNG declarado; ante un problema vuelve a KFM, lo cual puede esconder errores. El agente debe generar un **validador externo estricto** que falle con código != 0 y liste exactamente cada archivo/animación erróneo. No presentar fallback como evidencia de éxito.

**Nota sobre efectos, color y proporciones:** `CharacterRegistry.tint` actualmente tiñe visualmente al sprite; si el arte tiene sus propios colores, Codex debe ajustar el tinte de los personajes nuevos a blanco, preservando el tinte de KFM, y revisar capturas antes de decidir. Además `SPRITE_SCALE = 0.85` es compartido: preferir calibrar el render/anchor, y solo refactorizar la escala por personaje si una necesidad demostrada lo exige; mantener intacto el cuerpo físico y tests.

---

## 4. Etapas / gates: evitar gastar horas antes de validar

| Gate | Entregable mínimo | Aprobación necesaria para avanzar |
|---|---|---|
| G0 — Auditoría | Informe breve de Blender/Godot disponibles, inventario animaciones y rutas reales | No hay dependencias ocultas |
| G1 — Lookdev | `guitarist.blend`, rig, cámara, materiales, **una imagen frontal/perfil y una de combate**, vista de 128 px | Silueta reconocible, transparencia y pies visibles |
| G2 — Vertical slice | `idle`, `walk_fwd`, `stand_lp`, `hurt`, manifest y validador | Godot usa sprites propios (no fallback), golpes y hurtbox alineados |
| G3 — Personaje A | Todas las animaciones consumidas + revisión QA en movimiento | Combate normal vs CPU sin errores, sin intersecciones graves |
| G4 — Personaje B | Reuso del rig + modelo distinto + mismo pipeline | Pelea `guitarist` vs `frontman` completa |
| G5 — Pulido | Ajustes materiales, poses, looping y comparativas; documentación | Compilación/importación/test suite y capturas finales |

En cada gate: generar un **contact sheet** (mosaico de poses clave), registrar comandos exactos, errores y capturas. Si falla G1/G2, **corregir antes de generar los 25 sets de animación**. Preferir muestreo de poses clave y 4–8 frames por animación corta cuando corresponda; no multiplicar frames sin aportar legibilidad.

---

## 5. Prompts listos para pegar en Codex

### PROMPT 1 — Auditoría técnica y pipeline reproducible (ejecutar primero)

```text
Trabajá en este repositorio Rock Kombat. Leé íntegramente
docs/CODEX-BLENDER-PERSONAJES.md y assets/characters/README.md.
No me hagas instalar herramientas a ciegas. Primero inspeccioná:
- Blender (`blender --version`), Godot (`godot --version` o `godot4`),
  Python del sistema, git status y espacio disponible.
- core/character_frames.gd, core/character_registry.gd,
  core/kfm_frames.gd, fighter/fighter.gd, fighter/fighter.tscn,
  match/match.tscn, core/characters.gd, el manifest real de KFM
  y test/unit/test_character_registry.gd.

Objetivo: preparar pipeline Blender (bpy) -> PNG RGBA -> manifest.json
-> Godot SIN cambiar gameplay. Crear scripts Python idempotentes para:
1) generar .blend con rig/objetos/cámara/luces desde especificación;
2) renderizar acciones a carpetas de PNG numerados, manteniendo eje fijo;
3) construir manifest con durations de ticks a 60 fps;
4) validar dimensiones, alpha, nombres, consecutividad, duraciones,
   loop, presencia de idle y referencias a archivos;
5) generar un contact sheet y logs para revisión.

Definí comandos CLI simples en tools/blender/README.md.
Detectá Blender ejecutable de forma portable; usar argumentos `--`
para separar los de blender y los del script. No usés dependencia
externa si bpy y librería estándar alcanzan. No uses APIs de nube.

Entregá solo G0 + estructura G1, sin renderizar centenares de frames.
Reportá rutas, comandos ejecutados, qué validaste realmente y qué
queda pendiente. No cambies físicas, controles ni escenas de pelea.
Si faltan Blender o Godot, dejá scripts y verificadores listos, y
explicá el bloqueo sin inventar capturas o resultados.
```

### PROMPT 2 — El Guitarrista: modelo 3D original y prueba de 4 animaciones

```text
Continuá en Rock Kombat según docs/CODEX-BLENDER-PERSONAJES.md.
Conservá todos los cambios existentes. Completá G1 y G2 para
`guitarist` sin comenzar todavía `frontman`.

Modelá proceduralmente en Blender un guitarrista de plastilina
caricaturesca: cabeza grande, rostro expresivo, mechones volumétricos,
chaqueta oscura con acentos violeta/celeste, botas fuertes, guitarra
eléctrica ORIGINAL con correa. No copiar una persona real ni marca.

La vista final es un sprite de pelea 2D en un juego de 384x216.
Usá cámara ortográfica fija mirando al personaje de perfil levemente
frontal, orientación base a la derecha, key cálida y fill fría, fondo
transparente, roughness alta y detalles gruesos que funcionen a 100px.
Construí un rig reutilizable, jerarquía clara, acciones editables y
fuente .blend real guardada en repo.

Renderizá SOLO `idle`, `walk_fwd`, `stand_lp` y `hurt`.
Exportá RGBA con mismo lienzo, ancla de pies y encuadre para todas
las poses. Armá manifest según el formato de CharacterFrames; validá
cada PNG. Integrá `guitarist` en Godot y comprobá que el cargador
realmente eligió el arte nuevo (no KFM). El movimiento y golpe deben
conservar el timing del juego: NO ajustar frame data para acomodar
tu animación. Ajustá pose y muestreo al motor.

Producí contact sheet: idle, caminar, frame activo de golpe y reacción;
también una captura comparativa en la escena de recital. Si no podés
ejecutar Godot, marcá el test visual como no verificado y NO declares
éxito final. Actualizá tests de fallback que ahora deban esperar
arte disponible, sin eliminar la cobertura de fallback para un ID sin arte.

No produzcas las demás animaciones ni el segundo personaje antes de
resolver errores de carga, escala, transparencia, clip y ancla.
```

### PROMPT 3 — Completar animaciones del Guitarrista

```text
G1 y G2 del guitarrista están aprobados. Ahora completá G3.
Tomá los nombres y duraciones base del manifest KFM actual,
y los aliases que realmente utiliza Fighter. Para cada acción:
- storyboard de anticipación, acción, recuperación;
- poses del mismo rig, sin modificar cámara ni ancla;
- timing visual compatible con startup/active/recovery del gameplay;
- PNG numerados, RGBA, misma resolución; manifest actualizado;
- sin cambios en hitboxes, input, estadísticas ni IA.

Asegurá idle/caminata sin saltos de loop y acciones de bloqueo,
daño, caídas, agarres, puños, patadas y especiales con lectura
diferenciada. Mantené la guitarra visible cuando sea lógico y evitá
clipping serio contra la mano/cuerpo; usá controles o parentado en
animaciones para orientar el instrumento sin simulaciones complejas.
Generá solo acciones faltantes; cacheá renders existentes si fuente
y configuración no cambiaron. Corré validación estricta y tests Godot;
probá visualmente una ronda vs CPU. Entregá tabla de acciones, frames
renderizados, fallos y capturas/contact sheet. No arranques frontman
si el personaje A aún muestra defectos graves.
```

### PROMPT 4 — El Frontman: segundo luchador desde el rig reutilizable

```text
G3 del Guitarrista ya funciona. Implementá G4 para `frontman`.
Reutilizá la infraestructura de generación, rig, cámara, render,
validador y export. NO clones simplemente el aspecto del guitarrista.

Diseñá un cantante en plastilina con cabeza y mandíbula expresivas,
pelo alto en bloques, chaqueta corta coral/roja, guantes o brazaletes,
botas y micrófono de mano estilizado. Silueta y actitud distintas del
guitarrista: más agresivo, en constante movimiento. Mantener sprites
orientados a la derecha para que Godot pueda espejarlos.

Hacé primero idle/stand_lp/hurt y confirmá carga en Godot; después
exportá el resto según el manifest y estados realmente usados.
El ID está registrado como `frontman` y sus estadísticas existentes
deben permanecer intactas. Actualizá pruebas para cubrir dos fuentes
visuales independientes (SpriteFrames y ejes); inspeccioná ambas
escenas en combate a dos jugadores y vs CPU. No rehagas motor.
Presentá capturas de ambos luchadores enfrentados en el escenario.
```

### PROMPT 5 — QA, optimización y entrega final

```text
Terminaste ambos modelos y animaciones. Ejecutá G5 de
docs/CODEX-BLENDER-PERSONAJES.md. Verificá todos los PNG/manifest,
la existencia de fuente .blend, los loops, ancla constante, alpha,
coherencia de paleta y escala, sin enlaces faltantes a recursos.

Ejecutá importación Godot headless y la suite gdUnit4 indicada en
scripts/check-linux.sh. Revisá el test de fallback: debe comprobar
que un personaje sin recursos sigue usando KFM, mientras
guitarist/frontman cargan los suyos. Confirmá que HUD, rounds,
golpes, bloqueos, especiales, CPU y dos jugadores se comportan igual.

Agregá reporte resumido con comandos, cantidad de frames, tiempos
de generación, tamaño de archivos, resultado real de tests,
capturas de idle/golpe/daño y combate. Si un paso no pudo ejecutarse,
marcalo PENDIENTE. No inventes logs ni afirmes tests que no corriste.
No borres assets de KFM ni los créditos originales. Entregá todo
en commits claros; dejá main funcional.
```

---

## 6. Reglas de trabajo y control de calidad para Codex

**Seguridad del trabajo:** no sobrescribir cambios locales sin inspeccionar `git status`; no `git reset --hard`, `git clean -fd` ni borrados masivos. Trabajar en commits pequeños, ejecutar checks antes de fusionar. El usuario suele trabajar directamente en `main`: respetar esa preferencia si el árbol está limpio y el pedido así lo indica; no crear ramas innecesarias.

**No perder tiempo:**
- Prototipar a 1 personaje y 4 animaciones antes de producir el roster.
- Usar Blender `--background` y Python para reproducibilidad; no depender de clicks manuales en la UI para cada animación.
- Materiales y rig compartidos sin obligar a compartir silueta.
- Prohibido renderizar cientos de imágenes sin revisar primero 4 poses representativas.
- Evitar simulaciones costosas y herramientas de pago/nube.
- Reutilizar el set KFM **solo como referencia técnica**, no como arte final ni para pintar por encima de cada sprite.
- No integrar archivos gigantes de previews temporales en Git.

**Validaciones automáticas mínimas:**
- `manifest.json` JSON parseable y rutas seguras dentro del personaje.
- `idle` y todos los PNG declarados presentes; numeración consecutiva desde 000.
- Mismo canvas en todos los PNG, 4 canales, alpha con al menos píxeles transparentes y opacos.
- `axis` dentro del canvas, no cambiante entre frames.
- Duraciones positivas, cantidad consistente y `loop` booleano.
- Sin marcos totalmente transparentes ni brazos/cabeza sistemáticamente recortados.
- Comparación de proporción visual y boxes (F1 en Godot), con capturas.
- Prueba de fallback real y prueba de carga real de `guitarist` / `frontman` (no basta con que Godot no arroje errores).

**Comandos de chequeo previstos**, ajustar solo si difieren en el repo:

```bash
blender --version
godot --version || godot4 --version
bash scripts/check-linux.sh
godot --editor --path .
```

**Problema conocido a contemplar:** el test `test_unfinished_art_falls_back_to_kung_fu_man` de `test/unit/test_character_registry.gd` asume explícitamente que no existen los dos sets. Debe reemplazarse por tests que prueben contenido cargado y fallback en personaje sin recursos, no eliminarse sin sustitución.

**Formato de reporte al terminar cada fase:**

```text
FASE:
ARCHIVOS CREADOS/MODIFICADOS:
COMANDOS EJECUTADOS:
TESTS (aprobados/fallidos/no ejecutados):
CONTACT SHEET/CAPTURAS:
PROBLEMAS OBSERVADOS:
PENDIENTES:
COMMIT(S):
```

---

## 7. Prompt corto para iniciar otra sesión

> Abrí este repositorio y ejecutá **PROMPT 1** de `docs/CODEX-BLENDER-PERSONAJES.md`. Continuá secuencialmente por G0–G5, sin avanzar de fase hasta validar el entregable anterior. Priorizá un primer luchador jugable y visible sobre la cantidad de animaciones. No cambies el motor de pelea. Al finalizar cada fase, informá resultados reales y próximos pasos.

Si Codex trabaja en un contexto que permite ciclos autónomos largos, puede continuar automáticamente luego de cada **gate técnico comprobado**, pero nunca debe declarar una validación gráfica humana que no haya efectuado.
