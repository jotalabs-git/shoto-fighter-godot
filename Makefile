SHELL := /bin/bash

.PHONY: help check windows windows-debug

help:
	@echo "Rock Kombat"
	@echo "  make check          Ejecuta importación y tests de Godot (Linux)"
	@echo "  make windows        Exporta release Windows x86_64 desde Linux"
	@echo "  make windows-debug  Exporta debug Windows x86_64 desde Linux"

check:
	bash scripts/check-linux.sh

windows:
	bash scripts/export-windows.sh release

windows-debug:
	bash scripts/export-windows.sh debug
