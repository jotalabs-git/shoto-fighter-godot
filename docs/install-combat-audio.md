# Instalación y prueba de los paquetes de sonido

## Ya incluidos en main

Hay **17 OGG reales CC0 de Kenney** en `assets/audio/`: once efectos
conectados a ataques, golpes, agarres y caídas, más seis locuciones arcade.
Con solo actualizar el repositorio, el juego puede utilizarlos.

Los originales y el licenciamiento por fuente se enumeran en
[`assets/audio/CREDITS.md`](../assets/audio/CREDITS.md).
El menú contiene una pantalla **CREDITOS** con la atribución obligatoria
de la biblioteca de bart y un control **VOCES: ROCK / HUMOR**.

## Instalar el resto de las bibliotecas

```bash
git switch main
git pull --ff-only origin main

# En Ubuntu/Kubuntu, para abrir 7z y convertir los FLAC de Independent.nu:
sudo apt install p7zip-full ffmpeg

# Descarga e instala los cuatro paquetes elegidos:
python3 scripts/install_combat_audio.py

# Importar los archivos nuevos de sonido:
godot --headless --path . --editor --import --quit
godot --path .
```

El instalador descarga, extrae y conserva las bibliotecas completas en
`assets/audio/local/library/` (sin agregarlas a Git); copia un conjunto de
archivos a las claves que utiliza el juego. Esas copias generan un registro
`assets/audio/local/installed_manifest.json` con procedencia, asignación,
autor, licencia y SHA256.

Si el servidor de Kenney u OpenGameArt no acepta la descarga automática,
descargar desde las páginas oficiales y guardar estos archivos en
`assets/audio/local/downloads/`, o indicar `--archive-dir <ruta>`:

| Paquete | Nombre del archivo descargado |
|---|---|
| [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) | `kenney_impact-sounds.zip` |
| [Kenney Voiceover Pack Fighter](https://kenney.nl/assets/voiceover-pack-fighter) | `kenney_voiceover-pack-fighter.zip` |
| [37 hits/punches](https://opengameart.org/content/37-hitspunches) | `independent_nu_ljudbank-hits_and_punches.7z` |
| [24 cute fighting game voice recordings](https://opengameart.org/content/24-cute-fighting-game-voice-recordings) | `cute.zip` |

Por separado se pueden instalar:
```bash
python3 scripts/install_combat_audio.py --pack oga_cute
python3 scripts/install_combat_audio.py --pack oga_hits
```

**Voces humorísticas CC BY 3.0:** el instalador copia y renombra
hasta nueve tomas del archivo `cute.zip` para `guitarist`,
`frontman` y una voz neutra. Las asignaciones actuales son deterministas,
pero hay que escuchar los sonidos y seleccionar las mejores tomas para
cada reacción. El archivo original se mantiene sin edición en el directorio
local. La atribución de bart figura en **CREDITOS**, incluso si los
archivos no están instalados.

**Variaciones Kenney CC0:** al instalar el paquete completo Impact Sounds,
el script asigna once tomas adicionales `*_kenney` para alternarlas con las
ya incluidas en Git. Los restantes archivos quedan disponibles en la biblioteca
local para futuras selecciones.

**37 golpes CC0:** al instalar el archivo de Independent.nu, el script
convierte FLAC a WAV y asigna ocho variantes `*_oga`. El juego alterna
entre las grabaciones de Kenney y estas variantes.

## Sonniss, opcional y separado

El bundle de Sonniss 2026 es un recurso profesional de descarga extensa.
**No está incluido como archivos sueltos en Git**: su licencia prohíbe la
redistribución de sonidos aislados o como librería de assets. La descarga
y la selección de clips deben realizarse desde la fuente original, conforme
a los [términos vigentes](https://sonniss.com/gdc-bundle-license/).

Si ya se descargaron los archivos del bundle, para usar un par de clips
seleccionados y escuchados previamente:

```bash
python3 scripts/install_combat_audio.py --pack oga_cute \
  --sonniss-impact "/ruta/a/impacto.ogg" \
  --sonniss-fall "/ruta/a/caida.wav"
```

Los archivos de Sonniss quedan en `assets/audio/local/` (fuera de Git)
y entran como variantes adicionales. **No hay descarga ni selección
automática del bundle completo**.

## Verificación

```bash
bash scripts/check-linux.sh
godot --path .
```

Probar golpes ligeros, medios y fuertes; bloqueos; proyectiles; agarres
con primer plano y caídas. Las voces CC BY requieren elegir **VOCES: HUMOR**
en el menú y ejecutar el instalador primero. Si faltan archivos externos,
se mantienen las voces sintéticas originales.

**Validación pendiente:** las descargas externas y el resultado auditivo
no se pudieron verificar desde este entorno; las URL están basadas en
las páginas oficiales y pueden requerir descarga manual si cambian.
