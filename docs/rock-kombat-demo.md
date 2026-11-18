# Rock Kombat — baseline y primer prototipo

## Objetivo

Conservar el juego de lucha existente como punto de partida. Antes de incorporar músicos, comprobar en Linux que el proyecto importa, ejecuta la escena inicial y supera su batería de pruebas. La demo inicial será **dos jugadores en el mismo teclado**, con los luchadores y assets existentes.

## Estado auditado en el fork

- Motor: Godot 4, GDScript; README recomienda Godot 4.4+.
- Entrada principal: `res://ui/main_menu.tscn`, declarada en `project.godot`.
- Escena de combate: `res://match/match.tscn`.
- Arquitectura: `fighter/`, `core/`, `input/`, `match/`, `projectile/`, `fx/`, `ui/`.
- Controles P1: WASD; puños U/I/O; patadas J/K/L.
- Controles P2: flechas; puños ,/./; patadas N/M/B.
- El README contiene conteos de pruebas inconsistentes (78 y 98). No se considera ninguna cifra verificada hasta ejecutar el suite.
- Código MIT; los sprites de Kung Fu Man se documentan como CC BY-NC en `CREDITS.md`. No redistribuir como producto comercial sin revisar y reemplazar recursos.

## Reproducción en Linux

```bash
git clone https://github.com/jotalabs-git/shoto-fighter-godot.git
cd shoto-fighter-godot
bash scripts/check-linux.sh
godot --path . 
```

El ejecutable puede llamarse `godot4`; el script detecta ambos. Para abrir el editor: `godot --editor --path .` (o `godot4`). Se recomienda Godot 4.4 o posterior. El script falla si la importación o las pruebas fallan.

## Criterios para aprobar la demo base

1. La importación headless termina sin error.
2. La batería gdUnit4 finaliza sin fallos.
3. Se puede iniciar el menú y entrar a dos jugadores.
4. Ambos personajes se mueven, golpean y reciben daño, y la partida concluye normalmente.
5. Se confirma manualmente que no existen conflictos de teclas con el teclado local.

Los puntos 3–5 requieren prueba gráfica humana, no están cubiertos por el script.

## Próximo incremento después de aprobar la base

- Identidad provisional «Rock Kombat» sin tocar las reglas.
- Primer escenario musical y dos caricaturas **originales** con animaciones básicas.
- Mantener intactas hitboxes, lógica de rondas y tests salvo cambios necesarios y justificados.
- No incorporar música ni imágenes de terceros sin revisar sus licencias.

## Registro de verificación

- Inspección remota del repositorio y configuración: realizada.
- Ejecución de Godot y pruebas en este entorno: **no realizada** (no hay binario Godot disponible).
- Estado de aprobación: **pendiente de smoke test local**.
