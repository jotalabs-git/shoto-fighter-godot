# Rock Kombat — pase de identidad visual

Rama: `feat/rock-kombat-brand-palette` (basada en `main`).

## Colores oficiales

| Token | Hex | Uso |
|---|---|---|
| ROCK_RED | #FF003C | P2, impacto, acciones |
| STAGE_MAGENTA | #CC00FF | Brillo, bordes, ecualizador |
| NEON_BLUE | #00E5FF | P1, luces, título |
| AMP_YELLOW | #FFC400 | Timer, warnings, focos |
| METAL_SILVER | #C7C9D1 | Texto secundario |
| STAGE_BLACK | #0B0B12 | Fondo |

Los colores se centralizan en `globals/rock_brand.gd`.

## Superficies modificadas

- Menú: título bicolor, fondo de escenario nocturno, líneas neón y botones con estados visuales más fuertes.
- HUD: colores oficiales de ambas barras, marcas, temporizador, rounds y separadores; conserva su altura compacta.
- Escenario: reflectores cian/rojo/amarillo, barras de ecualizador cian-magenta-gris y acentos sutiles en el suelo.
- No se tocan físicas, cajas de colisión, controles, CPU ni sincronización.

## Verificación en Kubuntu

```bash
git fetch origin
git switch feat/rock-kombat-brand-palette
bash scripts/check-linux.sh
godot --path .
```

Comprobar que los botones normales, hover y pulsados se distinguen, que el HUD tiene buena lectura a 384×216, y que la iluminación no se confunde con los personajes. Probar resolución 1280×720 y ventana pequeña.

**Importante:** esta rama aplica la *paleta* y un tratamiento tipográfico con la fuente incorporada de Godot; no incorpora todavía el PNG del logo conceptual ni una tipografía licenciada externa. El logo generado durante la exploración no se considera un archivo fuente del proyecto hasta que se integre un asset optimizado y comprobado.

## Próximo paso de branding

Crear un logo transparente optimizado para pantalla de inicio y un emblema compacto; seleccionar una fuente Open Font License u otra licencia compatible, conservar sus avisos y agregarla al theme del juego sin sacrificar legibilidad.
