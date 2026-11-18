SHELL := /bin/bash

.PHONY: help check windows windows-debug windows-setup

help:
	@echo "Rock Kombat"
	@echo "  make check          Ejecuta importación y tests de Godot (Linux)"
	@echo "  make windows        Exporta release Windows x86_64 desde Linux"
	@echo "  make windows-debug  Exporta debug Windows x86_64 desde Linux"
	@echo "  make windows-setup  Instala las plantillas oficiales Windows de tu Godot"

check:
	bash scripts/check-linux.sh

windows:
	bash scripts/export-windows.sh release

windows-debug:
	bash scripts/export-windows.sh debug

windows-setup:
	@GODOT_BIN="$${GODOT:-$$(command -v godot || command -v godot4)}"; \
	if [[ -z "$$GODOT_BIN" ]]; then echo "Godot no está instalado" >&2; exit 127; fi; \
	python3 scripts/install-windows-templates.py "$$($$GODOT_BIN --version)"
