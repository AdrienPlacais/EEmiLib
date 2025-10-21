# Makefile for Sphinx documentation

SPHINXOPTS   ?=
SPHINXBUILD  ?= sphinx-build
SPHINXAPIDOC ?= sphinx-apidoc
SOURCEDIR     = .
BUILDDIR      = _build
SRC_DIR	      = ../src
EXCLUDE_DIR   = ../src/eemilib/experimental/*
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
	@echo "  html            Build HTML documentation"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf "$(BUILDDIR)"
	@if [ -d "$(APIDOC_DIR)" ]; then rm -rf "$(APIDOC_DIR)"/*; fi

apidoc:
	@echo "Generating API documentation..."
	@$(SPHINXAPIDOC) -o "$(APIDOC_DIR)" -d 5 -f -e -M "$(SRC_DIR)"
	@$(SPHINXAPIDOC) -o "$(APIDOC_DIR)" -d 5 -f -e -M "$(SRC_DIR)" "$(EXCLUDE_DIR)"
	@cd "$(APIDOC_DIR)" && perl -i -pe 's/^\S*\.(\S*) (package|module)/$$1 $$2/' *.rst

html:
	@echo "Building unversioned HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

%:
	@echo "Unknown target '$@'."
	@$(MAKE) help
