# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
WEBDIR        = ../plixlab/web
TESTOUTPUTDIR = ../tests/reference
STATICDIR     = $(SOURCEDIR)/_static/examples

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help copy-assets clean-assets Makefile

# Target to copy web and test output to _static
copy-assets:
	@echo "Copying web assets and test outputs to $(STATICDIR)..."
	@mkdir -p "$(STATICDIR)"
	@cp -r "$(WEBDIR)/." "$(STATICDIR)/"
	@cp -r "$(WEBDIR)/assets/js/load_standalone.js" "$(STATICDIR)/assets/js/load.js"
	@cp -r "$(TESTOUTPUTDIR)/." "$(STATICDIR)/references"
	@echo "Assets and test outputs copied."

# Optional target to clean the _static directory
clean-assets:
	@echo "Cleaning $(STATICDIR)..."
	@rm -rf "$(STATICDIR)"
	@echo "Cleaned."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option. $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile copy-assets
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
