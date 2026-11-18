# Diseño de audio — Rock Kombat

## Estado actual

La implementación en `fx/sfx.gd` genera efectos originales en memoria (PCM, 22.05 kHz, 16 bits) y los reproduce mediante **12 voces simultáneas**. No hace falta descargar ni redistribuir audio externo. Reemplaza al antiguo sintetizador con una única nota que cortaba el sonido anterior.

### Eventos y capas

| Evento | Efecto |
|---|---|
| Ataque de puño | Desplazamiento de aire corto |
| Ataque de patada | Desplazamiento de aire más grave y largo |
| Golpe conectado | Impacto ligero / medio / fuerte según movimiento |
| Barrido | Impacto bajo, contundente |
| Proyectil | Impacto energético diferente de los golpes físicos |
| Bloqueo | Impacto metálico/amortiguado |
| Inicio de agarre | Contacto breve + esfuerzo del atacante |
| Soltar víctima de agarre | Golpe de caída + reacción de la víctima |
| Derribo por barrido | Golpe de caída |
| K.O. | Golpe grave sostenido |
| Ataques y daño | Sonidos vocales sintéticos distintos para Guitarrista y Frontman |

Los esfuerzos de ataques fuertes siempre suenan; los de ataques ligeros se alternan para evitar saturación. Se añade variación sutil de tono para reducir la repetición. Los sonidos pueden solaparse sin cortar un efecto anterior.

La selección de impactos y personajes se hace en `fx/sound_profile.gd`. Los eventos `attack_cued`, `grab_cued` y `fall_cued` salen de `fighter/fighter.gd`; los impactos y bloqueos confirmados se oyen solo cuando la colisión se resuelve en `match/match_manager.gd`.

## Incorporar grabaciones reales (sin reescribir la lógica)

`Sfx` intenta cargar primero un recurso con la clave del evento bajo `assets/audio/`. Si no existe, genera el sonido procedural.

Ejemplos:
- `assets/audio/hit_punch_heavy.ogg`
- `assets/audio/hit_kick_medium.ogg`
- `assets/audio/fall.ogg`
- `assets/audio/voice_guitarist_effort_heavy.ogg`
- `assets/audio/voice_guitarist_hurt.ogg`
- `assets/audio/voice_frontman_effort_light.ogg`
- `assets/audio/voice_frontman_hurt.ogg`

Conviene grabar una **biblioteca de voces independiente** para cada luchador (esfuerzo corto, esfuerzo intenso, dolor, agarre), procesada y normalizada; los sonidos vocales generados aquí son **estilizados, no grabaciones humanas realistas**.

Antes de añadir archivos externos, comprobar uso comercial, redistribución, atribución y modificaciones permitidas. Preferir **CC0** o grabaciones propias y mantener procedencia/licencia junto al asset. El proyecto no necesita sonidos tomados de videojuegos ni películas comerciales.

## Verificación local

```bash
git switch main
git pull --ff-only
bash scripts/check-linux.sh
godot --path .
```

Probar con audio real (no `--audio-driver Dummy`):
1. Puños y patadas de tres intensidades; golpes que fallan solo deben producir movimiento de aire.
2. Bloqueo sin sonido de daño; proyectiles con timbre diferente.
3. Sujeción, golpe de caída al liberar la víctima y primer plano de cámara.
4. Alternar Guitarrista y Frontman como atacante para comprobar diferencia de voces.
5. Dos impactos casi simultáneos: ningún sonido debe silenciar al otro.
6. K.O. y reinicio de ronda; sin loops ni reproducción residual.

**Pendiente:** prueba auditiva de mezcla, volumen, clipping y calidad en hardware real, y sustitución opcional de gritos sintéticos por voces humanas originales o CC0.
