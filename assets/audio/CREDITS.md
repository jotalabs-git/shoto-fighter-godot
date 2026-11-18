# Audio — procedencia, licencias y atribuciones

Los archivos OGG versionados en `assets/audio/` están publicados por **Kenney**
bajo **Creative Commons CC0 1.0**. Se conservaron sus archivos originales y
se renombraron las copias seleccionadas para los eventos del juego.
No se modificó el audio. Atribución voluntaria:
- **Kenney — Impact Sounds**: https://kenney.nl/assets/impact-sounds
- **Kenney — Voiceover Pack (Fighter)**: https://kenney.nl/assets/voiceover-pack-fighter
- Licencia: https://creativecommons.org/publicdomain/zero/1.0/

## Atribución obligatoria para el paquete humorístico

> **“24 cute fighting game voice recordings”** por **bart**, publicado en
> **OpenGameArt.org**, licencia **Creative Commons Attribution 3.0 (CC BY 3.0)**.
> Fuente: https://opengameart.org/content/24-cute-fighting-game-voice-recordings
> Sitio solicitado expresamente por el creador: http://opengameart.org
> Licencia: https://creativecommons.org/licenses/by/3.0/

Las grabaciones de este paquete se **seleccionan, copian y renombran** para
asignarlas como esfuerzos y reacciones de Guitarrista/Frontman. No se realiza
edición del contenido sonoro con el instalador. Si después se mezclan, recortan,
procesan o modifican, actualizar este registro para indicar los cambios.
**Este crédito también está visible en la pantalla CREDITOS del juego.**
Los archivos del paquete humorístico se instalan localmente con
`python3 scripts/install_combat_audio.py --pack oga_cute`. No están
versionados en Git por el momento.

## Otra biblioteca CC0 opcional

- **“37 hits/punches”** por **Independent.nu**, publicado por qubodup:
  https://opengameart.org/content/37-hitspunches
- Licencia: CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/
- Los archivos de este paquete se asignan como variantes `*_oga` y alternan
  con el audio original de Kenney cuando están instalados.

## Sonniss: licencia propia, no CC0

- **Sonniss #GameAudioGDC Bundle**:
  https://gdc.sonniss.com/
- Condiciones vigentes: https://sonniss.com/gdc-bundle-license/
- Se pueden utilizar como audio sincronizado dentro de un videojuego y no
  requieren atribución, pero **no se pueden publicar los sonidos individuales
  como biblioteca de audio ni en un repositorio abierto de assets** sin
  autorización expresa. Los sonidos modificados conservan las restricciones.
- Para utilizar estos clips, descargar el paquete directamente de Sonniss,
  seleccionar manualmente el impacto y/o caída y usar las opciones
  `--sonniss-impact` / `--sonniss-fall` del instalador.
- Las importaciones de Sonniss permanecen en `assets/audio/local/`, que se
  excluye de Git. Verificar la licencia aplicable según la fecha de descarga.
- No utilizar estos recursos para entrenamiento de IA.

## Créditos dentro del juego

El menú principal contiene `CREDITOS`, que presenta las fuentes y enlaces.
El selector `VOCES: ROCK / HUMOR` permite utilizar el banco `bart`
cuando se instala. Si no hay archivos CC BY, el juego usa voces sintéticas
originales sin errores.

## Lista del audio Kenney incluido en Git (17 OGG)

| Destino en `assets/audio/` | Audio original Kenney |
|---|---|
| hit_punch_light.ogg | impactGeneric_light_000.ogg |
| hit_punch_medium.ogg | impactPunch_medium_000.ogg |
| hit_punch_heavy.ogg | impactPunch_heavy_000.ogg |
| hit_kick_light.ogg | impactGeneric_light_001.ogg |
| hit_kick_medium.ogg | impactPunch_medium_001.ogg |
| hit_kick_heavy.ogg | impactPunch_heavy_002.ogg |
| hit_sweep.ogg | impactWood_heavy_000.ogg |
| block.ogg | impactMetal_medium_000.ogg |
| grab.ogg | impactSoft_medium_000.ogg |
| fall.ogg | impactSoft_heavy_000.ogg |
| hit_energy.ogg | impactBell_heavy_000.ogg |
| announcer_round_1.ogg | round_1.ogg |
| announcer_round_2.ogg | round_2.ogg |
| announcer_round_3.ogg | round_3.ogg |
| announcer_fight.ogg | fight.ogg |
| announcer_winner.ogg | winner.ogg |
| announcer_game_over.ogg | game_over.ogg |

Origen binario de las copias CC0:
https://github.com/Mcamento8/open-game-sfx-index/tree/main/audio
(repositorio que conserva los audios de las bibliotecas originales de Kenney).
