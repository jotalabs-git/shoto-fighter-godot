# Exportar Rock Kombat para Windows desde Linux

Rock Kombat se desarrolla en **Godot 4 (GDScript)**. Para crear una
versión de Windows **no hace falta Wine, MinGW ni compilar el motor**.
Godot utiliza las plantillas oficiales de exportación de Windows.

## Requisitos

1. Editor Godot 4 compatible con este proyecto (actualmente Godot 4.7.x).
2. Plantillas de exportación de la **misma versión exacta** que el editor.
   En Godot: **Editor → Manage Export Templates → Download and Install**.
3. `make` y `bash` disponibles en Linux. No se necesita Python, Blender
   ni Windows para empaquetar los modelos GLB ya incluidos.

## Un comando

```bash
make windows
```

También existe:

```bash
make windows-debug
```

Y para verificar el juego local antes de exportar:

```bash
make check
```

Por defecto el script encuentra `godot` o `godot4` en PATH. Para indicar
una ruta propia del editor:

```bash
GODOT=/ruta/al/ejecutable/godot make windows
```

## Artefactos

El destino es `export/windows/` (ignorando el directorio en Git):

```
export/windows/
  RockKombat.exe
  RockKombat.pck
```

**Copiar ambos a la misma carpeta** en Windows; el PCK contiene escenas,
scripts, fuentes, audio, texturas, modelos 3D y otros recursos. No se activa
la opción `embed_pck` para mantener la exportación independiente del
formato de empaquetado del ejecutable.

El preset versionado en `export_presets.cfg` se llama `Windows Desktop`,
selecciona `x86_64` y exporta todos los recursos del proyecto.
El filtro `*.json` es **obligatorio** porque el juego usa
`FileAccess.open("res://assets/models/<personaje>.json")` para leer el
catálogo de animaciones y también JSON de los sprites de respaldo.
Sin ese filtro podrían funcionar los GLB pero fallar los personajes en el
juego exportado.

Los recursos privados instalados en `assets/audio/local/`, el código
fuente de Blender y los informes no forman parte de la distribución.
Los recursos públicos versionados en Git sí se incluyen según el preset.
Revisar los créditos y licencias antes de distribuir la versión.

## Comprobación

El script hace:

1. Identifica Godot y su versión.
2. Advierte si no encuentra las plantillas en la ruta estándar de Linux.
3. Importa recursos en modo headless (incluidos los GLB).
4. Exporta mediante `godot --headless --export-release "Windows Desktop"`.
5. Rechaza como error una exportación que no produzca **ambos** archivos.

Antes de publicar una versión, probar también en Windows real o una VM:

- Arranque, menú principal y pantalla de selección.
- Los **4 modelos 3D** y sus animaciones.
- Combates locales, CPU, sonidos, agarres y derribos.
- Que los catálogos JSON se puedan leer en Windows.
- Rendimiento con el backend gráfico **Compatibility / OpenGL**.

Un archivo `.exe` exportado desde Linux no queda automáticamente probado
en Windows: el comando verifica el empaquetado, no la ejecución en destino.

## Solución de problemas

- **No export templates found:** instalar las plantillas exactas en
  **Editor → Manage Export Templates** y reintentar.
- **No encuentra `godot`:** definir `GODOT=/ruta/al/binario`.
- **Import failed:** ejecutar `make check` para inspeccionar errores
  de modelos, animaciones o scripts.
- **Sin modelos en Windows:** verificar que los GLB y catálogos JSON estén
  en el export; el preset incluye explícitamente los JSON.
- **Windows no ejecuta el juego:** confirmar arquitectura x86_64,
  archivos `.exe` + `.pck` en la misma carpeta y soporte OpenGL del equipo.

Referencias oficiales:
- https://docs.godotengine.org/en/4.7/tutorials/export/exporting_projects.html
- https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_windows.html
