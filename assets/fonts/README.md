# Tipografías de Rock Kombat — SIL OFL 1.1

El juego utiliza tres familias de [Google Fonts](https://github.com/google/fonts), todas bajo **SIL Open Font License 1.1**. Sus licencias completas están versionadas en `assets/fonts/licenses/`.

| Uso | Fuente | Archivo instalado | Licencia |
|---|---|---|---|
| Títulos / logotipo tipográfico temporal | Metal Mania | `MetalMania-Regular.ttf` | `licenses/MetalMania-OFL.txt` |
| ROUND / FIGHT / K.O. | Bangers | `Bangers-Regular.ttf` | `licenses/Bangers-OFL.txt` |
| Menús, nombres, temporizador y HUD | Oxanium variable | `Oxanium-Variable.ttf` | `licenses/Oxanium-OFL.txt` |

## Instalación

Las fuentes binarias no se incluyen aún en Git. **Para ver la tipografía definitiva, hay que instalarlas una vez** desde la raíz del proyecto:

```bash
python3 scripts/install_fonts.py
godot --headless --path . --editor --import --quit
godot --path .
```

El instalador usa únicamente Python estándar. Descarga TTF desde el **repositorio oficial** `google/fonts`, comprueba el SHA exacto del blob Git esperado (no confía solamente en HTTPS) y guarda el archivo verificado en `assets/fonts/`.

Si las fuentes no existen, `RockBrand.font_file()` devuelve `null` y Godot usa la tipografía predeterminada: el juego debe seguir abriendo y siendo jugable sin conexión. El script puede volver a ejecutarse para verificar una instalación existente y no vuelve a descargar archivos válidos.

## Proveniencia verificable (Google Fonts, ruta `ofl/<familia>/`)

| Familia | Archivo de origen | Git blob SHA |
|---|---|---|
| metalmania | `MetalMania-Regular.ttf` | `db41a35fadc970e011bc076bba3f511160c80dde` |
| bangers | `Bangers-Regular.ttf` | `9b0f8c1f1b45e7bb4971b7d6a8604f9aacacdd32` |
| oxanium | `Oxanium[wght].ttf` | `ead485c7bf517197db91ef657614ac37d8007775` |

Repositorio: https://github.com/google/fonts/tree/main/ofl

La licencia OFL permite incluir las fuentes en un juego gratuito o comercial. Si se redistribuyen los TTF junto al juego, también deben distribuirse sus avisos de copyright y condiciones OFL correspondientes. No vender los archivos de fuentes como producto independiente ni incumplir las restricciones de nombres reservados al modificar fuentes.

**Distribución futura:** si se empaquetan las fuentes dentro de exportaciones Godot, conservar `licenses/` y un aviso en créditos. Los TTF descargados se pueden versionar después de completar la inspección y QA; no se debe depender del instalador en los equipos de los jugadores.

## QA visual

- Revisar título `ROCK KOMBAT` a resolución lógica **384 × 216**: sin recorte, separación y contraste.
- Probar los cuatro botones con teclado, ratón y mando; foco, hover y pulsado.
- Revisar que `EL GUITARRISTA` y `EL FRONTMAN` quepan en el HUD sin cruzar los marcadores de rondas.
- Comprobar valores del temporizador `99`, `10`, `0`; legibilidad y cambio de color.
- Verificar `ROUND 1`, `FIGHT!`, `K.O.` y los mensajes que use el motor, incluyendo sombra.
- Ejecutar `bash scripts/check-linux.sh` después de importar fuentes.
- Repetir el inicio de partida sin fuentes para comprobar el fallback.

**No confundir:** Metal Mania aplicada al título del menú es una solución tipográfica; el logo gráfico definitivo diseñado para la marca es un recurso aparte y aún debe integrarse si se desea.
