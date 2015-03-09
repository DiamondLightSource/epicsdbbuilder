# Specify defaults for testing
PREFIX := $(shell pwd)/prefix
PYTHON = dls-python
INSTALL_DIR = $(PREFIX)/lib/python2.7/site-packages
SCRIPT_DIR = $(PREFIX)/bin
MODULEVER=0.0

# Override with any release info
-include Makefile.private

# This is run when we type make
dist: setup.py $(wildcard epicsdbbuilder/*) make_docs
	MODULEVER=$(MODULEVER) $(PYTHON) setup.py bdist_egg
	touch dist

# Clean the module
clean:
	$(PYTHON) setup.py clean
	-rm -rf build dist *egg-info installed.files
	-find -name '*.pyc' -exec rm {} \;
	$(MAKE) -C docs clean

# Install the built egg
install: dist
	$(PYTHON) setup.py easy_install -m \
            --record=installed.files \
            --install-dir=$(INSTALL_DIR) \
            --script-dir=$(SCRIPT_DIR) dist/*.egg

make_docs:
	$(MAKE) -C docs
