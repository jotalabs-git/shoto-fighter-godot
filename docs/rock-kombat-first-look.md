# Primer pase visual — Rock Kombat

Esta rama cambia exclusivamente la presentación de `match/match.tscn` y `ui/hud.tscn`.

## Incluido
- Escenario de recital dibujado con Godot (sin imágenes externas): luces animadas, pantalla trasera con visualizador musical, truss, parlantes, siluetas del público y piso con perspectiva.
- Escenario extendido a ambos lados para tolerar el desplazamiento y zoom de cámara.
- HUD con cabecera oscura, barras de vida de alto contraste y placa para el temporizador.
- Conserva los sprites, animaciones, controles, valores de combate, colisiones, IA y reglas de rondas originales.
- Parte de la rama `fix/clean-first-match-presentation`, por lo que las cajas de entrenamiento se ocultan de manera predeterminada. F1 las alterna.

## Probar localmente

```bash
git fetch origin
git switch feat/rock-kombat-stage-hud
godot --editor --path .
```

Ejecutar F5, elegir 2 Players o vs CPU, comprobar:
1. El escenario cubre el viewport durante el desplazamiento de cámara.
2. El HUD muestra salud/tiempo/rondas y sus barras decrecen correctamente.
3. Las luces no distraen del combate ni ocultan personajes.
4. F1 activa y desactiva las cajas de depuración.
5. La jugabilidad se mantiene idéntica.

También ejecutar `bash scripts/check-linux.sh` si se fusionó la preparación Linux del PR #1, o directamente:

```bash
godot --headless --path . --editor --import --quit
godot --headless --path . -s addons/gdUnit4/bin/GdUnitCmdTool.gd --ignoreHeadlessMode -a res://test
```

**Validación pendiente:** no se dispone de un ejecutable Godot en el entorno de autoría. Requiere revisión visual y pruebas locales en Kubuntu.
