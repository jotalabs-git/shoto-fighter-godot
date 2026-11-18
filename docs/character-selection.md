# Selección de personajes — Rock Kombat

La pantalla `ui/character_select.tscn` usa **cuatro modelos GLB originales** y una
presentación arcade que muestra a los dos luchadores completos, de pie,
reproduciendo su animación `idle` en sendos `SubViewport` 3D.

## Plantel actual

| ID | Nombre | Modelo |
|---|---|---|
| `guitarist` | El Guitarrista | `assets/models/guitarist.glb` |
| `frontman` | El Frontman | `assets/models/frontman.glb` |
| `ozzy` | Ozzy Osbourne | `assets/models/ozzy.glb` |
| `bruce` | Bruce Dickinson | `assets/models/bruce.glb` |

Cada modelo tiene su catálogo `assets/models/<id>.json` (47 clips declarados).
La pantalla no precocina imágenes: instancia el GLB y reproduce su clip
`idle` mediante `AnimationPlayer`. Para añadir luchadores en el futuro,
actualizar `core/character_registry.gd`, proporcionar el GLB con `idle`
y su JSON de combate, y ampliar el roster.

## Flujo

- Menú principal: elegir Versus local o dificultad de CPU.
- Versus local: cada jugador controla su cursor y confirma por separado.
- Contra CPU: P1 selecciona, el rival se elige automáticamente entre
  personajes distintos. Los dos visores siguen mostrando modelos 3D.
- Se permiten combates espejo en versus local.
- Tras confirmar, `GameConfig.set_characters` conserva los IDs;
  `MatchManager._enter_tree` los asigna antes de que los fighters inicialicen
  estadísticas, animaciones y sonido.

### Teclas

| | Mover | Confirmar |
|---|---|---|
| P1 | WASD | U (puño débil) o J (patada débil) |
| P2 | Flechas | coma (puño débil) o N (patada débil) |

**Esc**: desconfirmar P1 o volver al menú.

## Diseño y rendimiento

- Dos `SubViewportContainer` con un mundo 3D aislado para cada vista previa.
- Cámara ortográfica y luces propias, sin interferir con la cámara de combate.
- Resolución interna de vista previa 354×330, escalada al área de pantalla.
- El modelo anterior se elimina al cambiar la selección.
- Si el modelo no está disponible, se muestra un mensaje y el juego
  conserva el fallback ya existente de `Fighter`.

## Comprobación

```bash
git switch main
git pull --ff-only origin main
bash scripts/check-linux.sh
godot --path .
```

Verificar visualmente: cuatro selecciones distintas; que los modelos miren
hacia el centro, estén de pie y respiren; que los controles P1 y P2 sean
independientes; espejo P1/P2; CPU aleatoria diferente; y que el combatiente
correspondiente aparezca en combate sin romper sonido, cámara ni hitboxes.

El test `test/integration/test_character_select.gd` valida el registro,
las previsualizaciones y la propagación de IDs al combate.
