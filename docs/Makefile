# Makefile for Sphinx documentation

SPHINXOPTS   ?=
SPHINXBUILD  ?= sphinx-build
SPHINXAPIDOC ?= sphinx-apidoc
SOURCEDIR     = .
BUILDDIR      = ../../eemilib-docs/
SRC_DIR	      = ../src
APIDOC_DIR    = eemilib

.PHONY: help clean apidoc html
.DEFAULT_GOAL := help

help:
	@echo "Usage: make [TARGET]"
	@echo ""
	@echo "Available targets:"
	@echo "  help            Show this help message"
	@echo "  clean           Clean build artifacts"
	@echo "  apidoc          Generate API documentation"
	@echo "  html            Build unversioned HTML documentation"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf "$(BUILDDIR)"
	@if [ -d "$(APIDOC_DIR)" ]; then rm -rf "$(APIDOC_DIR)"/*; fi

apidoc:
	@echo "Generating API documentation..."
	@$(SPHINXAPIDOC) -o "$(APIDOC_DIR)" -d 5 -f -e -M "$(SRC_DIR)"

html:
	@echo "Building unversioned HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

%:
	@echo "Unknown target '$@'."
	@$(MAKE) help
